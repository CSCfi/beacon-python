"""Prepare mate."""
from functools import partial
from ..utils.logging import LOG
from ..api.exceptions import BeaconServerError
from .handover import add_handover
from ..utils.data_query import handle_wildcard, transform_misses, transform_record
from .. import __handover_drs__
from typing import Tuple, List, Optional


async def fetch_fusion_dataset(db_pool, assembly_id, position, chromosome, reference, mate, datasets=None, access_type=None, misses=False):
    """Execute filter datasets.

    There is an Uber query that aims to retrieve specific for data for mate fusion table.
    """
    # Take one connection from the database pool
    async with db_pool.acquire(timeout=180) as connection:
        # Start a new session with the connection
        async with connection.transaction():
            # Fetch dataset metadata according to user request
            datasets_query = None if not datasets else datasets
            access_query = None if not access_type else access_type

            start_pos = None if position[0] is None or (position[2] and position[3]) else position[0]
            end_pos = None if position[1] is None or (position[4] and position[5]) else position[1]
            startMax_pos = position[3]
            startMin_pos = position[2]
            endMin_pos = position[4]
            endMax_pos = position[5]

            refbase = None if not reference else handle_wildcard(reference)
            try:
                if misses:
                    # For MISS and ALL. We have already found all datasets with matching variants,
                    # so now just get one post per accessible, remaining datasets.
                    query = """SELECT DISTINCT ON (datasetId)
                               datasetId as "datasetId", accessType as "accessType",
                               $4 as "referenceName", False as "exists"
                               FROM beacon_dataset_table
                               WHERE coalesce(accessType = any($2::access_levels[]), true)
                               AND assemblyId=$3
                               AND coalesce(datasetId = any($1::varchar[]), false);
                               """
                    statement = await connection.prepare(query)
                    db_response = await statement.fetch(datasets_query, access_query, assembly_id, chromosome)

                else:
                    # UBER QUERY - TBD if it is what we need
                    # referenceBases, alternateBases and variantType fields are NOT part of beacon's specification response
                    query = """SELECT a.datasetId as "datasetId", b.accessType as "accessType", a.chromosome as "referenceName",
                                a.reference as "referenceBases", a.alternate as "alternateBases", a.chromosomeStart as "start",
                                a.mate as "mateName",
                                a.chromosomePos as "referenceID", a.matePos as "mateID", a.mateStart as "mateStart", a.mateStart as "end",
                                b.externalUrl as "externalUrl", b.description as "note",
                                a.alleleCount as "variantCount", CAST('BND' as text) as "variantType",
                                a.callCount as "callCount", b.sampleCount as "sampleCount",
                                a.frequency, True as "exists"
                                FROM beacon_dataset_table b, beacon_mate_table a
                                WHERE a.datasetId=b.datasetId
                                AND b.assemblyId=$3
                                AND a.chromosome=$12
                                AND coalesce(a.mate=$4, true)
                                AND coalesce(a.reference LIKE any($5::varchar[]), true)
                                AND coalesce(a.mateStart=$7, true)
                                AND ($6::integer IS NULL OR a.chromosomeStart=$6)
                                AND ($8::integer IS NULL OR a.chromosomeStart<=$8) AND ($9::integer IS NULL OR a.chromosomeStart>=$9)
                                AND ($10::integer IS NULL OR a.mateStart>=$10) AND ($11::integer IS NULL OR a.mateStart<=$11)
                                AND coalesce(b.accessType = any($2::access_levels[]), true)
                                AND coalesce(a.datasetId = any($1::varchar[]), true)
                                UNION
                                SELECT
                                a.datasetId as "datasetId", b.accessType as "accessType", a.chromosome as "referenceName",
                                a.reference as "referenceBases", a.alternate as "alternateBases", a.chromosomeStart as "start",
                                a.mate as "mateName",
                                a.chromosomePos as "referenceID", a.matePos as "mateID", a.mateStart as "mateStart", a.mateStart as "end",
                                b.externalUrl as "externalUrl", b.description as "note",
                                a.alleleCount as "variantCount", CAST('BND' as text) as "variantType",
                                a.callCount as "callCount", b.sampleCount as "sampleCount",
                                a.frequency, True as "exists"
                                FROM beacon_dataset_table b, beacon_mate_table a
                                WHERE a.datasetId=b.datasetId
                                AND b.assemblyId=$3
                                AND a.mate=$12
                                AND coalesce(a.chromosome=$4, true)
                                AND coalesce(a.reference LIKE any($5::varchar[]), true)
                                AND coalesce(a.mateStart=$6, true)
                                AND ($7::integer IS NULL OR a.chromosomeStart=$7)
                                AND ($8::integer IS NULL OR a.mateStart<=$8) AND ($9::integer IS NULL OR a.mateStart>=$9)
                                AND ($10::integer IS NULL OR a.chromosomeStart>=$10) AND ($11::integer IS NULL OR a.chromosomeStart<=$11)
                                AND coalesce(b.accessType = any($2::access_levels[]), true)
                                AND coalesce(a.datasetId = any($1::varchar[]), false);
                                """
                statement = await connection.prepare(query)
                db_response = await statement.fetch(
                    datasets_query, access_query, assembly_id, mate, refbase, start_pos, end_pos, startMax_pos, startMin_pos, endMin_pos, endMax_pos, chromosome
                )
                LOG.info(f"Query for dataset(s): {datasets} that are {access_type} matching conditions.")
                datasets = []
                for record in list(db_response):
                    processed = transform_misses(record) if misses else transform_record(record)
                    if __handover_drs__:
                        # If handover feature is enabled, add handover object to response
                        processed = add_handover(processed)
                    datasets.append(processed)
                return datasets
            except Exception as e:
                raise BeaconServerError(f"Query dataset DB error: {e}")


async def find_fusion(
    db_pool,
    assembly_id: str,
    position: Tuple[Optional[int], ...],
    chromosome: str,
    reference: str,
    mate: str,
    dataset_ids: List[str],
    access_type: List,
    include_dataset: str,
) -> List:
    """Find datasets based on filter parameters.

    This also takes into consideration the token value as to establish permissions.
    """
    hit_datasets = []
    miss_datasets = []
    response = []
    fetch_call = partial(fetch_fusion_dataset, db_pool, assembly_id, position, chromosome, reference, mate)
    hit_datasets = await fetch_call(dataset_ids, access_type)
    if include_dataset in ["ALL", "MISS"]:
        accessible_missing = set(dataset_ids).difference([item["datasetId"] for item in hit_datasets])
        miss_datasets = await fetch_call(accessible_missing, access_type, misses=True)

    response = hit_datasets + miss_datasets
    return response

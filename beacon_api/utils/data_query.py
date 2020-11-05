"""Query DB and prepare data for response."""

from datetime import datetime
from functools import partial
from typing import Dict, List, Optional

from typing import Tuple
from .logging import LOG
from ..api.exceptions import BeaconServerError
from ..extensions.handover import add_handover
from .. import __handover_drs__


def transform_record(record) -> Dict:
    """Format the record we got from the database to adhere to the response schema."""
    response = dict(record)
    response["referenceBases"] = response.pop("referenceBases")  # NOT part of beacon specification
    response["alternateBases"] = response.pop("alternateBases")  # NOT part of beacon specification
    response["variantType"] = response.pop("variantType")  # NOT part of beacon specification
    response["start"] = response.pop("start")  # NOT part of beacon specification
    response["end"] = response.pop("end")  # NOT part of beacon specification
    response["frequency"] = 0 if response.get("frequency") is None else round(response.pop("frequency"), 9)
    response["variantCount"] = 0 if response.get("variantCount") is None else response.get("variantCount")
    response["info"] = {"accessType": response.pop("accessType")}
    # Error is not required and should not be shown unless exists is null
    # If error key is set to null it will still not validate as it has a required key errorCode
    # Setting this will make schema validation fail
    # response["error"] = None

    return response


def transform_misses(record) -> Dict:
    """Format the missed datasets record we got from the database to adhere to the response schema."""
    response = dict(record)
    response["referenceBases"] = ""  # NOT part of beacon specification
    response["alternateBases"] = ""  # NOT part of beacon specification
    response["variantType"] = ""  # NOT part of beacon specification
    response["start"] = 0  # NOT part of beacon specification
    response["end"] = 0  # NOT part of beacon specification
    response["frequency"] = 0
    response["variantCount"] = 0
    response["callCount"] = 0
    response["sampleCount"] = 0
    response["info"] = {"accessType": response.pop("accessType")}
    # Error is not required and should not be shown unless exists is null
    # If error key is set to null it will still not validate as it has a required key errorCode
    # Setting this will make schema validation fail
    # response["error"] = None

    return response


def transform_metadata(record) -> Dict:
    """Format the metadata record we got from the database to adhere to the response schema."""
    response = dict(record)
    response["info"] = {"accessType": response.pop("accessType")}
    if "createDateTime" in response and isinstance(response["createDateTime"], datetime):
        response["createDateTime"] = response.pop("createDateTime").strftime("%Y-%m-%dT%H:%M:%SZ")
    if "updateDateTime" in record and isinstance(response["updateDateTime"], datetime):
        response["updateDateTime"] = response.pop("updateDateTime").strftime("%Y-%m-%dT%H:%M:%SZ")

    return response


async def fetch_datasets_access(db_pool, datasets: Optional[List]):
    """Retrieve CONTROLLED datasets."""
    public = []
    registered = []
    controlled = []
    async with db_pool.acquire(timeout=180) as connection:
        async with connection.transaction():
            datasets_query = None if not datasets else datasets
            try:
                query = """SELECT accessType, datasetId FROM beacon_dataset_table
                           WHERE coalesce(datasetId = any($1::varchar[]), true);
                           """
                statement = await connection.prepare(query)
                db_response = await statement.fetch(datasets_query)
                for record in list(db_response):
                    if record["accesstype"] == "PUBLIC":
                        public.append(record["datasetid"])
                    if record["accesstype"] == "REGISTERED":
                        registered.append(record["datasetid"])
                    if record["accesstype"] == "CONTROLLED":
                        controlled.append(record["datasetid"])
                return public, registered, controlled
            except Exception as e:
                raise BeaconServerError(f"Query available datasets DB error: {e}")


async def fetch_dataset_metadata(db_pool, datasets=None, access_type=None):
    """Execute query for returning dataset metadata.

    We use a DB View for this.
    """
    # Take one connection from the database pool
    async with db_pool.acquire(timeout=180) as connection:
        # Start a new session with the connection
        async with connection.transaction():
            # Fetch dataset metadata according to user request
            datasets_query = None if not datasets else datasets
            access_query = None if not access_type else access_type
            try:
                query = """SELECT datasetId as "id", name as "name", accessType as "accessType",
                           externalUrl as "externalUrl", description as "description",
                           assemblyId as "assemblyId", variantCount as "variantCount",
                           callCount as "callCount", sampleCount as "sampleCount",
                           version as "version", createDateTime as "createDateTime",
                           updateDateTime as "updateDateTime"
                           FROM dataset_metadata WHERE
                           coalesce(datasetId = any($1::varchar[]), true)
                           AND coalesce(accessType = any($2::access_levels[]), true);
                           """
                statement = await connection.prepare(query)
                db_response = await statement.fetch(datasets_query, access_query)
                metadata = []
                LOG.info(f"Query for dataset(s): {datasets} metadata that are {access_type}.")
                for record in list(db_response):
                    metadata.append(transform_metadata(record))
                return metadata
            except Exception as e:
                raise BeaconServerError(f"Query metadata DB error: {e}")


def handle_wildcard(sequence) -> List:
    """Construct PostgreSQL friendly wildcard string."""
    if "N" in sequence:
        # Wildcard(s) found, use wildcard notation
        return [f"%{sequence.replace('N', '_')}%"]
    else:
        # No wildcard(s) found, use standard notation
        return [sequence]


async def fetch_filtered_dataset(db_pool, assembly_id, position, chromosome, reference, alternate, datasets=None, access_type=None, misses=False):
    """Execute filter datasets.

    There is an Uber query that aims to be all inclusive.
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

            variant = None if not alternate[0] else alternate[0]
            altbase = None if not alternate[1] else handle_wildcard(alternate[1])
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
                               a.reference as "referenceBases", a.alternate as "alternateBases", a.start as "start", a.end as "end",
                               b.externalUrl as "externalUrl", b.description as "note",
                               a.alleleCount as "variantCount", a.variantType as "variantType",
                               a.callCount as "callCount", b.sampleCount as "sampleCount",
                               a.frequency, True as "exists"
                               FROM beacon_data_table a, beacon_dataset_table b
                               WHERE a.datasetId=b.datasetId
                               AND b.assemblyId=$3
                               AND ($8::integer IS NULL OR a.start=$8)
                               AND ($9::integer IS NULL OR a.end=$9)
                               AND ($10::integer IS NULL OR a.start<=$10) AND ($11::integer IS NULL OR a.start>=$11)
                               AND ($12::integer IS NULL OR a.end>=$12) AND ($13::integer IS NULL OR a.end<=$13)
                               AND coalesce(a.reference LIKE any($7::varchar[]), true)
                               AND coalesce(a.variantType=$5, true)
                               AND coalesce(a.alternate LIKE any($6::varchar[]), true)
                               AND a.chromosome=$4
                               AND coalesce(b.accessType = any($2::access_levels[]), true)
                               AND coalesce(a.datasetId = any($1::varchar[]), false);
                               """

                    statement = await connection.prepare(query)
                    db_response = await statement.fetch(
                        datasets_query,
                        access_query,
                        assembly_id,
                        chromosome,
                        variant,
                        altbase,
                        refbase,
                        start_pos,
                        end_pos,
                        startMax_pos,
                        startMin_pos,
                        endMin_pos,
                        endMax_pos,
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


def filter_exists(include_dataset: str, datasets: List) -> List[str]:
    """Return those datasets responses that the `includeDatasetResponses` parameter decides.

    Look at the exist parameter in each returned dataset to established HIT or MISS.
    """
    data = []
    if include_dataset == "ALL":
        data = datasets
    elif include_dataset == "NONE":
        data = []
    elif include_dataset == "HIT":
        data = [d for d in datasets if d["exists"] is True]
    elif include_dataset == "MISS":
        data = [d for d in datasets if d["exists"] is False]

    return data


async def find_datasets(
    db_pool,
    assembly_id: str,
    position: Tuple[Optional[int], ...],
    chromosome: str,
    reference: str,
    alternate: Tuple,
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
    fetch_call = partial(fetch_filtered_dataset, db_pool, assembly_id, position, chromosome, reference, alternate)
    hit_datasets = await fetch_call(dataset_ids, access_type)
    if include_dataset in ["ALL", "MISS"]:
        accessible_missing = set(dataset_ids).difference([item["datasetId"] for item in hit_datasets])
        miss_datasets = await fetch_call(accessible_missing, access_type, misses=True)

    response = hit_datasets + miss_datasets
    return response

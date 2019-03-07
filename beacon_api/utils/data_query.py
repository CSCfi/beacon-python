"""Query DB and prepare data for reponse."""

from datetime import datetime
from .logging import LOG
from ..api.exceptions import BeaconServerError
from ..conf.config import DB_SCHEMA


# def transform_record(record, variantCount):
def transform_record(record):
    """Format the record we got from the database to adhere to the response schema."""
    response = dict(record)
    response["referenceBases"] = response.pop("referenceBases")  # NOT part of beacon specification
    response["alternateBases"] = response.pop("alternateBases")  # NOT part of beacon specification
    response["variantType"] = response.pop("variantType")  # NOT part of beacon specification
    response["frequency"] = round(response.pop("frequency"), 9)
    response["info"] = {"accessType": response.pop("accessType")}
    # Error is not required and should not be shown unless exists is null
    # If error key is set to null it will still not validate as it has a required key errorCode
    # otherwise schema validation will fail
    # response["error"] = None

    return response


def transform_misses(record):
    """Format the missed datasets record we got from the database to adhere to the response schema."""
    response = dict(record)
    response["referenceBases"] = ''  # NOT part of beacon specification
    response["alternateBases"] = ''  # NOT part of beacon specification
    response["variantType"] = ''  # NOT part of beacon specification
    response["frequency"] = 0
    response["variantCount"] = 0
    response["callCount"] = 0
    response["sampleCount"] = 0
    response["info"] = {"accessType": response.pop("accessType")}
    # Error is not required and should not be shown unless exists is null
    # If error key is set to null it will still not validate as it has a required key errorCode
    # otherwise schema validation will fail
    # response["error"] = None

    return response


def transform_metadata(record):
    """Format the metadata record we got from the database to adhere to the response schema."""
    response = dict(record)
    response["info"] = {"accessType": response.pop("accessType")}
    if 'createDateTime' in response and isinstance(response["createDateTime"], datetime):
        response["createDateTime"] = response.pop("createDateTime").strftime('%Y-%m-%dT%H:%M:%SZ')
    if 'updateDateTime' in record and isinstance(response["updateDateTime"], datetime):
        response["updateDateTime"] = response.pop("updateDateTime").strftime('%Y-%m-%dT%H:%M:%SZ')

    return response


async def fetch_datasets_access(db_pool, datasets):
    """Retrieve CONTROLLED datasets."""
    public = []
    registered = []
    controlled = []
    async with db_pool.acquire(timeout=180) as connection:
        async with connection.transaction():
            # datasets_query = "TRUE" if not datasets else f"datasetId IN {sql_tuple(datasets)}"
            datasets_query = None if not datasets else datasets
            try:
                query = f"""SELECT accessType, datasetId FROM {DB_SCHEMA}beacon_dataset_table
                            WHERE coalesce(datasetId = any($1::varchar[]), true);"""
                statement = await connection.prepare(query)
                db_response = await statement.fetch(datasets_query)
                for record in list(db_response):
                    if record['accesstype'] == 'PUBLIC':
                        public.append(record['datasetid'])
                    if record['accesstype'] == 'REGISTERED':
                        registered.append(record['datasetid'])
                    if record['accesstype'] == 'CONTROLLED':
                        controlled.append(record['datasetid'])
                return public, registered, controlled
            except Exception as e:
                raise BeaconServerError(f'Query available datasets DB error: {e}')


async def fetch_dataset_metadata(db_pool, datasets=None, access_type=None):
    """Execute query for returning dataset metadata.

    We use a DB View for this.
    """
    # Take one connection from the database pool
    async with db_pool.acquire(timeout=180) as connection:
        # Start a new session with the connection
        async with connection.transaction():
            # Fetch dataset metadata according to user request
            # datasets_query = "TRUE" if not datasets else f"a.datasetId IN {sql_tuple(datasets)}"
            datasets_query = None if not datasets else datasets
            # access_query = "TRUE" if not access_type else f"b.accesstype IN {sql_tuple(access_type)}"
            access_query = None if not access_type else access_type
            try:
                query = f"""SELECT datasetId as "id", name as "name", accessType as "accessType",
                            externalUrl as "externalUrl", description as "description",
                            assemblyId as "assemblyId", variantCount as "variantCount",
                            callCount as "callCount", sampleCount as "sampleCount",
                            version as "version", createDateTime as "createDateTime",
                            updateDateTime as "updateDateTime"
                            FROM {DB_SCHEMA}dataset_metadata WHERE
                            coalesce(datasetId = any($1::varchar[]), true)
                            AND coalesce(accessType = any($2::varchar[]), true);"""
                statement = await connection.prepare(query)
                db_response = await statement.fetch(datasets_query, access_query)
                metadata = []
                LOG.info(f"Query for dataset(s): {datasets} metadata that are {access_type}.")
                for record in list(db_response):
                    metadata.append(transform_metadata(record))
                return metadata
            except Exception as e:
                raise BeaconServerError(f'Query metadata DB error: {e}')


def handle_wildcard(sequence):
    """Construct PostgreSQL friendly wildcard string."""
    if 'N' in sequence:
        # Wildcard(s) found, use wildcard notation
        return [f"%{sequence.replace('N', '_')}%"]
    else:
        # No wildcard(s) found, use standard notation
        return [sequence]


async def fetch_filtered_dataset(db_pool, assembly_id, position, chromosome, reference, alternate,
                                 datasets=None, access_type=None, misses=False):
    """Execute filter datasets.

    There is an Uber query that aims to be all inclusive.
    """
    # Take one connection from the database pool
    async with db_pool.acquire(timeout=180) as connection:
        # Start a new session with the connection
        async with connection.transaction():
            # Fetch dataset metadata according to user request
            # datasets_query = "TRUE" if not datasets else f"a.datasetId IN {sql_tuple(datasets)}"
            datasets_query = None if not datasets else datasets
            # access_query = "TRUE" if not access_type else f"b.accesstype IN {sql_tuple(access_type)}"
            access_query = None if not access_type else access_type

            start_pos = None if position[0] is None or (position[2] and position[3]) else position[0]
            end_pos = None if position[1] is None or (position[4] and position[5]) else position[1]
            startMax_pos = None if position[3] is None else position[3]
            startMin_pos = None if position[2] is None else position[2]
            endMin_pos = None if position[4] is None else position[4]
            endMax_pos = None if position[5] is None else position[5]

            variant = None if not alternate[0] else alternate[0]
            altbase = None if not alternate[1] else handle_wildcard(alternate[1])
            refbase = None if not reference else handle_wildcard(reference)
            try:

                # UBER QUERY - TBD if it is what we need
                # referenceBases, alternateBases and variantType fields are NOT part of beacon specification example response
                query = f"""SELECT {"DISTINCT ON (a.datasetId)" if misses else ''} a.datasetId as "datasetId", b.accessType as "accessType",
                            a.chromosome as "referenceName", a.reference as "referenceBases", a.alternate as "alternateBases",
                            b.externalUrl as "externalUrl", b.description as "note",
                            a.alleleCount as "variantCount", a.variantType as "variantType",
                            a.callCount as "callCount", b.sampleCount as "sampleCount",
                            a.frequency, {"FALSE" if misses else "TRUE"} as "exists"
                            FROM {DB_SCHEMA}beacon_data_table a, {DB_SCHEMA}beacon_dataset_table b
                            WHERE a.datasetId=b.datasetId
                            AND b.assemblyId=$3
                            AND {"NOT" if misses else ''} (coalesce(a.start=$8, true)
                            AND coalesce(a.end=$9, true)
                            AND coalesce(a.start<=$10, true) AND coalesce(a.start>=$11, true)
                            AND coalesce(a.end>=$12, true) AND coalesce(a.end<=$13, true)
                            AND coalesce(a.reference LIKE any($7::varchar[]), true)
                            AND coalesce(a.variantType=$5, true)
                            AND coalesce(a.alternate LIKE any($6::varchar[]), true))
                            AND a.chromosome=$4
                            AND coalesce(b.accessType = any($2::varchar[]), true)
                            {"<>" if misses and datasets else "AND"} coalesce(a.datasetId = any($1::varchar[]), true) ;"""
                datasets = []
                statement = await connection.prepare(query)
                db_response = await statement.fetch(datasets_query, access_query, assembly_id, chromosome,
                                                    variant, altbase, refbase,
                                                    start_pos, end_pos,
                                                    startMax_pos, startMin_pos,
                                                    endMin_pos, endMax_pos)
                LOG.info(f"Query for dataset(s): {datasets} that are {access_type} matching conditions.")
                for record in list(db_response):
                    processed = transform_misses(record) if misses else transform_record(record)
                    datasets.append(processed)
                return datasets
            except Exception as e:
                raise BeaconServerError(f'Query dataset DB error: {e}')


def filter_exists(include_dataset, datasets):
    """Return those datasets responses that the `includeDatasetResponses` parameter decides.

    Look at the exist parameter in each returned dataset to established HIT or MISS.
    """
    if include_dataset == 'ALL':
        return datasets
    elif include_dataset == 'NONE':
        return []
    elif include_dataset == 'HIT':
        return [d for d in datasets if d['exists'] is True]
    elif include_dataset == 'MISS':
        return [d for d in datasets if d['exists'] is False]


async def find_datasets(db_pool, assembly_id, position, chromosome, reference, alternate, dataset_ids, access_type, include_dataset):
    """Find datasets based on filter parameters.

    This also takes into consideration the token value as to establish permissions.
    """
    hit_datasets = []
    miss_datasets = []
    response = []
    hit_datasets = await fetch_filtered_dataset(db_pool, assembly_id, position, chromosome, reference, alternate,
                                                dataset_ids, access_type)
    if include_dataset in ['ALL', 'MISS']:
        miss_datasets = await fetch_filtered_dataset(db_pool, assembly_id, position, chromosome, reference, alternate,
                                                     [item["datasetId"] for item in hit_datasets],
                                                     access_type, misses=True)

    response = hit_datasets + miss_datasets
    return response

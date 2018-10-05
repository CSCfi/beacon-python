from datetime import datetime
from .logging import LOG


def sql_tuple(array):
    if len(array) > 1:
        return f"({str(tuple(array))})"
    elif len(array) == 1:
        return "(\'" + array[0] + "\')"


def transform_record(record):
    response = dict(record)
    response["frequency"] = round(response.pop("frequency"), 9)
    response["info"] = [{"accessType": response.pop("accessType")}]
    response["error"] = None

    return response

async def fetch_dataset_metadata(db_pool, datasets=None, access_type=None):
    # Take one connection from the database pool
    async with db_pool.acquire() as connection:
        # Start a new session with the connection
        async with connection.transaction():
            # Fetch dataset metadata according to user request
            # TO DO Test that datasets=[] and access_type=[] work with 1..n items
            datasets_query = "TRUE" if not datasets else f"a.dataset_id IN {sql_tuple(datasets)}"
            access_query = "TRUE" if not access_type else f"b.accesstype IN {sql_tuple(access_type)}"
            try:
                db_response = await connection.fetch(f"""SELECT * FROM dataset_metadata WHERE
                                                     ({datasets_query}) AND ({access_query});""")
                metadata = []
                for record in list(db_response):
                    # Format postgres timestamptz into string for JSON serialisation
                    parsed_record = {key: (value.strftime('%Y-%m-%dT%H:%M:%SZ') if isinstance(value, datetime) else value)
                                     for key, value in dict(record).items()}
                    metadata.append(parsed_record)
                return metadata
            except Exception:
                raise Exception


async def fetch_filtered_dataset(db_pool, position, alternate, datasets=None, access_type=None):
    async with db_pool.acquire() as connection:
        # Start a new session with the connection
        async with connection.transaction():
            # Fetch dataset metadata according to user request
            # TO DO Test that datasets=[] and access_type=[] work with 1..n items
            datasets_query = "TRUE" if not datasets else f"a.dataset_id IN {sql_tuple(datasets)}"
            access_query = "TRUE" if not access_type else f"b.accesstype IN {sql_tuple(access_type)}"

            start_pos = "TRUE" if position[0] == 0 else f"a.start>={position[0]}"
            end_pos = "TRUE" if position[1] == 0 else f"a.end<={position[1]}"
            startMax_pos = "TRUE" if position[2] == 0 else f"a.start<={position[2]}"
            startMin_pos = "TRUE" if position[3] == 0 else f"a.start>={position[3]}"
            endMin_pos = "TRUE" if position[4] == 0 else f"a.end>={position[4]}"
            endMax_pos = "TRUE" if position[5] == 0 else f"a.end<={position[5]}"

            variant = 'TRUE' if not alternate[0] else 'a.type=\'' + alternate[0] + '\''
            altbase = 'TRUE' if not alternate[1] else 'a.alternate=\'' + alternate[1] + '\''
            try:
                # TO DO Should just a result be dataset be returned or all finds in datasets ?
                # The Distinct is here as we one to return only one result per dataset
                # That is not an OK approach and needs to be rethinked as the API is not clear on this
                # Or this example dataset used here is faulty and the values need to be caculated in a VIEW
                query = f"""SELECT DISTINCT ON (a.dataset_id) a.dataset_id as "datasetID", b.accessType as "accessType",
                            b.externalUrl as "externalUrl", b.description as "note",
                            b.assemblyId as "assemblyId", a.variantcount as "variantCount",
                            a.callcount as "callCount", a.samplecount as "sampleCount",
                            a.frequency, TRUE as "exists"
                            FROM beacon_data_table a, beacon_dataset_table b
                            WHERE a.dataset_id=b.dataset_id
                            AND {datasets_query} AND {access_query}
                            AND {start_pos} AND {end_pos}
                            AND {startMax_pos} AND {startMin_pos}
                            AND {endMin_pos} AND {endMax_pos}
                            AND {variant} AND {altbase};"""
                datasets = []
                # TO DO test id this gives inconsistent results on database change
                statement = await connection.prepare(query)
                db_response = await statement.fetch()
                for record in list(db_response):
                    datasets.append(transform_record(record))
                return datasets
            except Exception:
                raise Exception


def filter_exists(include_dataset, datasets):
    """Return those datasets responses that the `includeDatasetResponses` parameter decides.

    More Description.
    """
    if include_dataset == 'ALL':
        return datasets
    elif include_dataset == 'NONE':
        return []
    elif include_dataset == 'HIT':
        return list(filter(lambda d: d['exists'] is True, datasets))
    elif include_dataset == 'MISS':
        return list(filter(lambda d: d['exists'] is False, datasets))


async def find_datasets(db_pool, position, alternate, dataset_ids, token):
    # for now we only check if there is a token
    # we will bona_fide_status and the actual permissions
    access_type = "PUBLIC" if not token else None
    response = await fetch_filtered_dataset(db_pool, position, alternate,
                                            datasets=dataset_ids, access_type=[access_type])
    return response

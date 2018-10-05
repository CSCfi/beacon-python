from datetime import datetime
from .logging import LOG


def sql_tuple(array):
    """Transform array to SQL tupleself.

    Special case if array is of length 1.
    """
    if len(array) > 1:
        return f"{str(tuple(array))}"
    elif len(array) == 1:
        return "(\'" + array[0] + "\')"


def transform_record(record):
    """Format the record we got from the database to adhere to the response schema."""
    response = dict(record)
    response["frequency"] = round(response.pop("frequency"), 9)
    response["info"] = [{"accessType": response.pop("accessType")}]
    response["error"] = None

    return response


def transform_misses(record):
    """Format the missed datasets record we got from the database to adhere to the response schema."""
    response = dict(record)
    response["frequency"] = 0
    response["variantCount"] = 0
    response["callCount"] = 0
    response["sampleCount"] = 0
    response["info"] = [{"accessType": response.pop("accessType")}]
    response["error"] = None

    return response


def transform_metadata(record):
    """Format the metadata record we got from the database to adhere to the response schema."""
    response = dict(record)
    response["info"] = [{"accessType": response.pop("accessType")}]
    # TO DO test with null date
    if 'createDateTime' in response and isinstance(response["createDateTime"], datetime):
        response["createDateTime"] = response.pop("createDateTime").strftime('%Y-%m-%dT%H:%M:%SZ')
    # TO DO test with null date
    if 'updateDateTime' in record and isinstance(response["updateDateTime"], datetime):
        response["updateDateTime"] = response.pop("updateDateTime").strftime('%Y-%m-%dT%H:%M:%SZ')

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
                query = f"""SELECT  dataset_id as "id", name as "name", accessType as "accessType",
                            externalUrl as "externalUrl", description as "description",
                            assemblyId as "assemblyId", variantcount as "variantCount",
                            callcount as "callCount", samplecount as "sampleCount",
                            version as "version", createdatetime as "createDateTime",
                            updatedatetime as "updateDateTime"
                            FROM dataset_metadata WHERE
                            ({datasets_query}) AND ({access_query});"""
                # TO DO test id this gives inconsistent results on database change
                statement = await connection.prepare(query)
                db_response = await statement.fetch()
                metadata = []
                for record in list(db_response):
                    # Format postgres timestamptz into string for JSON serialisation
                    # parsed_record = {key: (value.strftime('%Y-%m-%dT%H:%M:%SZ') if isinstance(value, datetime) else value)
                    #                  for key, value in dict(record).items()}
                    metadata.append(transform_metadata(record))
                return metadata
            except Exception:
                raise Exception


async def fetch_filtered_dataset(db_pool, position, alternate, datasets=None, access_type=None, misses=False):
    # Take one connection from the database pool
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

                # UBER QUERY - TBD if it is what we need
                query = f"""SELECT DISTINCT ON (a.dataset_id) a.dataset_id as "datasetId", b.accessType as "accessType",
                            b.externalUrl as "externalUrl", b.description as "note",
                            a.variantcount as "variantCount",
                            a.callcount as "callCount", a.samplecount as "sampleCount",
                            a.frequency, {"FALSE" if misses else "TRUE"} as "exists"
                            FROM beacon_data_table a, beacon_dataset_table b
                            WHERE a.dataset_id=b.dataset_id
                            AND {access_query} {"<>" if misses else "AND"} {datasets_query}
                            AND {"NOT" if misses else ''} ({start_pos} AND {end_pos}
                            AND {startMax_pos} AND {startMin_pos}
                            AND {endMin_pos} AND {endMax_pos}
                            AND {variant} AND {altbase});"""
                datasets = []
                # TO DO test id this gives inconsistent results on database change
                statement = await connection.prepare(query)
                db_response = await statement.fetch()
                for record in list(db_response):
                    processed = transform_misses(record) if misses else transform_record(record)
                    datasets.append(processed)
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
    access_type = ["REGISTERED", "PUBLIC"] if not token else ["PUBLIC"]
    hit_datasets = await fetch_filtered_dataset(db_pool, position, alternate,
                                                dataset_ids, access_type)
    miss_datasets = await fetch_filtered_dataset(db_pool, position, alternate,
                                                 [item["datasetId"] for item in hit_datasets],
                                                 access_type, misses=True)

    response = hit_datasets + miss_datasets
    return response
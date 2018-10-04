from datetime import datetime
from .logging import LOG


async def fetch_dataset_metadata(pool, datasets=None, access_type=None):
    # Take one connection from the database pool
    async with pool.acquire() as connection:
        # Start a new session with the connection
        async with connection.transaction():
            # Fetch dataset metadata according to user request
            # TO DO Test that datasets=[] and access_type=[] work with 1..n items
            # TO DO This query with optional will not work
            db_response = await connection.fetch(f"""SELECT * FROM dataset_metadata
                                                 {'' if not datasets else str(tuple(datasets))}
                                                 {'' if not access_type else str(tuple(access_type))};""")
            metadata = []
            for record in list(db_response):
                # Format postgres timestamptz into string for JSON serialisation
                parsed_record = {key: (value.strftime('%Y-%m-%dT%H:%M:%SZ') if isinstance(value, datetime) else value) for key, value in dict(record).items()}
                metadata.append(parsed_record)
            return metadata


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


def find_datasets(request, token):
    pass

# def position(start, end, startMin, startMax, endMin, endMax):
#     """Check the values of the position parameters (start, startMin, startMax, end, endMain, endMax).
#
#     The `position()` function returns a position list `pos` that depending on the submitted parameters, either have one, two or four items.
#
#     :type start: Integer
#     :param start: The parameter `start` given in the request.
#     :type end: Integer
#     :param end: The parameter `end` given in the request.
#     :type stertMin: Integer
#     :param startMin: The parameter `startMin` given in the request.
#     :type startMax: Integer
#     :param startMax: The parameter `startMax` given in the request.
#     :type endMin: Integer
#     :param endMin: The parameter `endMin` given in the request.
#     :type endMax: Integer
#     :param endMax: The parameter `endMax` given in the request.
#     :type pos: Array
#     :return pos: An array containing the parameters that where given, the length depends on how many parameters where in the request.
#     """
#     pos = []
#     if start != 0:
#         if end != 0:
#             # start --> end
#             pos.append(start)
#             pos.append(end)
#             return pos
#         else:
#             # only start
#             pos.append(start)
#             return pos
#     # fuzzy boundaries
#     if startMin != 0 and startMax != 0 and endMin != 0 and endMax != 0:
#         pos.append(startMin)
#         pos.append(startMax)
#         pos.append(endMin)
#         pos.append(endMax)
#         return pos
#
#
# def alleleFind(datasetId, chromosome, position, allele, variantType):
#     """Query the database with the submitted parameters and checks if it finds the allele in the right place.
#
#     The `alleleFind()` function returns True if found and False if not. It also returns the object to the row that was queried in the database.
#
#     :type datasetId: String
#     :param datasetId: The name of the data set.
#     :type chromosome: String
#     :param chromosome: The chromosome given in the `referenceName` parameter in the request.
#     :type position:
#     :param position: Array of the positional arguments given in the request.
#     :type allele: String
#     :param allele: The alternate allele tha`t is queried for.
#     :type variantType:
#     :param variantType: The variant type given in the request.
#     :return boolean: The True or False answer from the query.
#     :return row: The row from the database that has been queried.
#     """
#     # if alternateBases or variantType are not defined they are set to None
#     logging.info(' * Opening connection to database')
#     conn = psycopg2.connect(DB_URL)
#     cur = conn.cursor()
#
#     if allele == '0':
#         if len(position) == 1:
#             logging.debug(' * Execute SQL query: SELECT * FROM genomes WHERE dataset_id={} AND chromosome={} AND start={} AND  type={}'
#                           .format(datasetId, chromosome, position[0], variantType))
#             cur.execute('SELECT * FROM genomes WHERE dataset_id=%s AND chromosome=%s AND start=%s AND  type=%s',
#                         [datasetId, chromosome, position[0], variantType])
#         elif len(position) == 2:
#             logging.debug(' * Execute SQL query: SELECT * FROM genomes WHERE dataset_id={} AND chromosome={} AND start={} AND "end"={} AND type={}'
#                           .format(datasetId, chromosome, position[0], position[1], variantType))
#             cur.execute('SELECT * FROM genomes WHERE dataset_id=%s AND chromosome=%s AND start=%s AND "end"=%s AND type=%s',
#                         [datasetId, chromosome, position[0], position[1], variantType])
#         else:
#             logging.debug(' * Execute SQL query: SELECT * FROM genomes WHERE dataset_id={} AND chromosome={} AND start>={} AND start<={} AND "end">={} AND \
#             "end"<={} AND type={}'.format(datasetId, chromosome, position[0], position[1], position[2], position[3], variantType))
#             cur.execute('SELECT * FROM genomes WHERE dataset_id=%s AND chromosome=%s AND start>=%s AND start<=%s AND "end">=%s AND "end"<=%s AND type=%s',
#                         [datasetId, chromosome, position[0], position[1], position[2], position[3], variantType])
#     elif allele != '0':
#         if len(position) == 1:
#             logging.debug(' * Execute SQL query: SELECT * FROM genomes WHERE dataset_id={} AND chromosome={} AND start={} AND  alternate={}'
#                           .format(datasetId, chromosome, position[0], allele))
#             cur.execute('SELECT * FROM genomes WHERE dataset_id=%s AND chromosome=%s AND start=%s AND  alternate=%s',
#                         [datasetId, chromosome, position[0], allele])
#         elif len(position) == 2:
#             logging.debug(' * Execute SQL query: SELECT * FROM genomes WHERE dataset_id={} AND chromosome={} AND start={} AND "end"={} AND alternate={}'
#                           .format(datasetId, chromosome, position[0], position[1], allele))
#             cur.execute('SELECT * FROM genomes WHERE dataset_id=%s AND chromosome=%s AND start=%s AND "end"=%s AND alternate=%s',
#                         [datasetId, chromosome, position[0], position[1], allele])
#         else:
#             logging.debug(' * Execute SQL query: SELECT * FROM genomes WHERE dataset_id={} AND chromosome={} AND start>={} AND start<={} AND "end">={} AND \
#             "end"<={}AND alternate={}'.format(datasetId, chromosome, position[0], position[1], position[2], position[3], allele))
#             cur.execute(
#                 'SELECT * FROM genomes WHERE dataset_id=%s AND chromosome=%s AND start>=%s AND start<=%s AND "end">=%s AND "end"<=%s AND alternate=%s',
#                 [datasetId, chromosome, position[0], position[1], position[2], position[3], allele])
#
#     row = cur.fetchone()
#     logging.debug(' * First matching row from query: {}'.format(row))
#     logging.info(' * Closing connection to database')
#     conn.close()
#
#     if row is None:
#         logging.debug(' * Returning FALSE')
#         return False, row
#     else:
#         logging.debug(' * Returning TRUE')
#         return True, row
#
#
# def datasetAlleleResponseBuilder(datasetId, referenceName, pos, alternateBases, variantType, BeaconDataset):
#     """
#     Call the `alleleFind()` function and receives the answer to the exist parameter and the database object to the row in the database.
#
#     If `exists` == False the function sets the `variantCount`, `sampleCount`,
#     `callCount` and `frequency` to 0. And if `exists` == True the function gets the parameter values from the database.
#
#     :type datasetId: String
#     :param datasetId: The name of the data set.
#     :type referenceName:
#     :param referenceName: Reference name (chromosome). Accepting values 1-22, X, Y so follows Ensembl chromosome naming convention.
#     :type pos: Array
#     :param pos: Array of the positional arguments given in the request.
#     :type alternateBases: String
#     :param alternateBases: The bases that appear instead of the reference bases, given in the request.
#     :type variantType: String
#     :param variantType: The variant type given in the request.
#     :type BeaconDataset: Array
#     :param BeaconDataset: Array of the names of the data sets in the database.
#     :type datasetAlleleResponse: Dict
#     :return: datasetAlleleResponse: Dict of the response that has been constructed.
#     """
#     error = None
#     j = 0
#     for i in BeaconDataset:
#         if datasetId in i['name']:
#             break
#         j += 1
#
#     logging.info(' * Calling function alleleFind()')
#     exists, row = alleleFind(datasetId, referenceName, pos, alternateBases, variantType)
#     logging.info(' * Returning from function alleleFind()')
#
#     if not exists:
#         variantCount, sampleCount, callCount, frequency = 0, 0, 0, 0  # does not alter the database only the representation
#     else:
#         frequency = row[12]
#         sampleCount = row[11]
#         callCount = row[10]
#         variantCount = row[9]
#
#     datasetAlleleResponse = {
#         'datasetId': datasetId,
#         'exists': exists,
#         'frequency': frequency,
#         'variantCount': variantCount,
#         'callCount': callCount,
#         'sampleCount': sampleCount,
#         'note': BeaconDataset[j]['description'],
#         'externalUrl': BeaconDataset[j]['externalUrl'],
#         'info': BeaconDataset[j]['info'],
#         'error': error
#     }
#     logging.info(' * Returning datasetAlleleResponse')
#     return datasetAlleleResponse
#
#
# def checkParameters(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId, datasetIds,
#                     includeDatasetResponses, error_):
#     datasetresponses = ['ALL', 'HIT', 'MISS', 'NONE']
#     datasetAlleleResponses = []
#     datasetIds_list = []
#     Beacon = constructor() # WHY ? FIX this
#     BeaconDataset = Beacon['dataset']
#     for dset in BeaconDataset:
#         datasetIds_list.append(dset['name'])
#
#     pos = position(start, end, startMin, startMax, endMin, endMax)
#     logging.debug(' * The position() function returned the array: {}'.format(pos))
#
#     # check if start/startMin parameter is missing
#     _check_start_end(start, startMin, startMax, end, endMin, endMax, error_)
#
#     # check assembly and reference bases
#     _check_basses(referenceBases, alternateBases, variantType, error_)
#
#     # check if assemblyId is missing
#     _check_assembly(assemblyId, error_)
#
#     # check if includeDataserResponses is missing
#     if includeDatasetResponses not in datasetresponses:
#         # if an error occurs the 'exists' must be 'null'
#         for set in datasetAlleleResponses:
#             set['exists'] = None
#         logging.warning(' * ERROR BAD REQUEST: includeDatasetResponses not valid')
#         error_.bad_request('includeDatasetResponses not valid')
#
#     # checks if there are datasetIds given. If there are, then check if the the datasetIds are in the database Table.
#     # If not give ERROR. If they are correct, build a response for each data set that is correct.
#
#     # if no data sets where given, it will query all data sets in the database
#
#
#     # creates empty lists for specific datasetResponses
#     false_datasetAlleleResponses = []
#     true_datasetAlleleResponses = []
#     # fills the lists with the responses
#     for response in datasetAlleleResponses:
#         if not response['exists']:
#             false_datasetAlleleResponses.append(response)
#         elif response['exists']:
#             true_datasetAlleleResponses.append(response)
#
#     return datasetAlleleResponses, true_datasetAlleleResponses, false_datasetAlleleResponses, includeDatasetResponses

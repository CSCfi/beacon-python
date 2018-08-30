import logging
import beacon_info
import psycopg2
import os


def position(start, end, startMin, startMax, endMin, endMax):
    """
    The `position()` function checks the values of the position parameters (start, startMin, startMax, end, endMain, endMax)
    and returns a position list `pos` that depending on the submitted parameters, either have one, two or four items.

    :type start: Integer
    :param start: The parameter `start` given in the request.
    :type end: Integer
    :param end: The parameter `end` given in the request.
    :type stertMin: Integer
    :param startMin: The parameter `startMin` given in the request.
    :type startMax: Integer
    :param startMax: The parameter `startMax` given in the request.
    :type endMin: Integer
    :param endMin: The parameter `endMin` given in the request.
    :type endMax: Integer
    :param endMax: The parameter `endMax` given in the request.
    :type pos: Array
    :return pos: An array containing the parameters that where given, the length depends on how many parameters where in the request.
    """
    pos = []
    if start != 0:
        if end != 0:
            # start --> end
            pos.append(start)
            pos.append(end)
            return pos
        else:
            # only start
            pos.append(start)
            return pos
    # fuzzy boundaries
    if startMin != 0 and startMax != 0 and endMin != 0 and endMax != 0:
        pos.append(startMin)
        pos.append(startMax)
        pos.append(endMin)
        pos.append(endMax)
        return pos


def alleleFind(datasetId, chromosome, position, allele, variantType):
    """
    The `alleleFind()` function queries the database with the submitted parameters and checks if it finds the allele in the right place.
    It returns True if found and False if not. It also returns the object to the row that was queried in the database.

    :type datasetId: String
    :param datasetId: The name of the data set.
    :type chromosome: String
    :param chromosome: The chromosome given in the `referenceName` parameter in the request.
    :type position:
    :param position: Array of the positional arguments given in the request.
    :type allele: String
    :param allele: The alternate allele tha`t is queried for.
    :type variantType:
    :param variantType: The variant type given in the request.
    :return boolean: The True or False answer from the query.
    :return row: The row from the database that has been queried.
    """
    url = os.environ['DATABASE_URL'].split('/')
    POSTGRES = {
        'user': os.environ['DATABASE_USER'],
        'password': os.environ['DATABASE_PASSWORD'],
        'database': os.environ['DATABASE_NAME'],
        'host': url[2],
    }
    DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES['user'], pw=POSTGRES['password'], url=POSTGRES['host'], db=POSTGRES['database'])
    # if alternateBases or variantType are not defined they are set to None
    logging.info(' * Opening connection to database')
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    if allele == '0':
        if len(position) == 1:
            logging.debug(' * Execute SQL query: SELECT * FROM genomes WHERE dataset_id={} AND chromosome={} AND start={} AND  type={}'
                          .format(datasetId, chromosome, position[0], variantType))
            cur.execute('SELECT * FROM genomes WHERE dataset_id=%s AND chromosome=%s AND start=%s AND  type=%s',
                        [datasetId, chromosome, position[0], variantType])
        elif len(position) == 2:
            logging.debug(' * Execute SQL query: SELECT * FROM genomes WHERE dataset_id={} AND chromosome={} AND start={} AND "end"={} AND type={}'
                          .format(datasetId, chromosome, position[0], position[1], variantType))
            cur.execute('SELECT * FROM genomes WHERE dataset_id=%s AND chromosome=%s AND start=%s AND "end"=%s AND type=%s',
                        [datasetId, chromosome, position[0], position[1], variantType])
        else:
            logging.debug(' * Execute SQL query: SELECT * FROM genomes WHERE dataset_id={} AND chromosome={} AND start>={} AND start<={} AND "end">={} AND \
            "end"<={} AND type={}'.format(datasetId, chromosome, position[0], position[1], position[2], position[3], variantType))
            cur.execute('SELECT * FROM genomes WHERE dataset_id=%s AND chromosome=%s AND start>=%s AND start<=%s AND "end">=%s AND "end"<=%s AND type=%s',
                        [datasetId, chromosome, position[0], position[1], position[2], position[3], variantType])
    elif allele != '0':
        if len(position) == 1:
            logging.debug(' * Execute SQL query: SELECT * FROM genomes WHERE dataset_id={} AND chromosome={} AND start={} AND  alternate={}'
                          .format(datasetId, chromosome, position[0], allele))
            cur.execute('SELECT * FROM genomes WHERE dataset_id=%s AND chromosome=%s AND start=%s AND  alternate=%s',
                        [datasetId, chromosome, position[0], allele])
        elif len(position) == 2:
            logging.debug(' * Execute SQL query: SELECT * FROM genomes WHERE dataset_id={} AND chromosome={} AND start={} AND "end"={} AND alternate={}'
                          .format(datasetId, chromosome, position[0], position[1], allele))
            cur.execute('SELECT * FROM genomes WHERE dataset_id=%s AND chromosome=%s AND start=%s AND "end"=%s AND alternate=%s',
                        [datasetId, chromosome, position[0], position[1], allele])
        else:
            logging.debug(' * Execute SQL query: SELECT * FROM genomes WHERE dataset_id={} AND chromosome={} AND start>={} AND start<={} AND "end">={} AND \
            "end"<={}AND alternate={}'.format(datasetId, chromosome, position[0], position[1], position[2], position[3], allele))
            cur.execute(
                'SELECT * FROM genomes WHERE dataset_id=%s AND chromosome=%s AND start>=%s AND start<=%s AND "end">=%s AND "end"<=%s AND alternate=%s',
                [datasetId, chromosome, position[0], position[1], position[2], position[3], allele])

    row = cur.fetchone()
    logging.debug(' * First matching row from query: {}'.format(row))
    logging.info(' * Closing connection to database')
    conn.close()

    if row is None:
        logging.debug(' * Returning FALSE')
        return False, row
    else:
        logging.debug(' * Returning TRUE')
        return True, row


def datasetAlleleResponseBuilder(datasetId, referenceName, pos, alternateBases, variantType, BeaconDataset):
    """
    The `datasetAlleleResponseBuilder()` function calls the `alleleFind()` function and receives the answer to the exist parameter
    and the database object to the row in the database. If `exists` == False the function sets the `variantCount`, `sampleCount`,
    `callCount` and `frequency` to 0. And if `exists` == True the function gets the parameter values from the database.

    :type datasetId: String
    :param datasetId: The name of the data set.
    :type referenceName:
    :param referenceName: Reference name (chromosome). Accepting values 1-22, X, Y so follows Ensembl chromosome naming convention.
    :type pos: Array
    :param pos: Array of the positional arguments given in the request.
    :type alternateBases: String
    :param alternateBases: The bases that appear instead of the reference bases, given in the request.
    :type variantType: String
    :param variantType: The variant type given in the request.
    :type BeaconDataset: Array
    :param BeaconDataset: Array of the names of the data sets in the database.
    :type datasetAlleleResponse: Dict
    :return: datasetAlleleResponse: Dict of the response that has been constructed.
    """
    error = None
    j = 0
    for i in BeaconDataset:
        if datasetId in i['name']:
            break
        j += 1

    logging.info(' * Calling function alleleFind()')
    exists, row = alleleFind(datasetId, referenceName, pos, alternateBases, variantType)
    logging.info(' * Returning from function alleleFind()')

    if not exists:
        variantCount, sampleCount, callCount, frequency = 0, 0, 0, 0  # does not alter the database only the representation
    else:
        frequency = row[12]
        sampleCount = row[11]
        callCount = row[10]
        variantCount = row[9]

    datasetAlleleResponse = {
        'datasetId': datasetId,
        'exists': exists,
        'frequency': frequency,
        'variantCount': variantCount,
        'callCount': callCount,
        'sampleCount': sampleCount,
        'note': BeaconDataset[j]['description'],
        'externalUrl': BeaconDataset[j]['externalUrl'],
        'info': BeaconDataset[j]['info'],
        'error': error
    }
    logging.info(' * Returning datasetAlleleResponse')
    return datasetAlleleResponse


def checkParameters(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId, datasetIds,
                    includeDatasetResponses, error_):
    """
    The `checkParameters()` function validates the submitted parameters values and checks if required parameters are missing.
    It calls the appropriate `BeaconError` method if something is wrong.

    :type referenceName: String
    :param referenceName: Reference name (chromosome). Accepting values 1-22, X, Y so follows Ensembl chromosome naming convention.
    :type start: Integer
    :param start:
            I. START ONLY:

            - for single positions, e.g. the `start` of a specified sequence alteration where the size is given through the specified `alternateBases`
            - typical use are queries for SNV and small InDels
            - the use of `start` without an `end` parameter requires the use of `referenceBases`
            II. START AND END:

            - special use case for exactly determined structural changes
    :type startMin: Integer
    :param startMin: Minimum start coordinate
            - startMin + startMax + endMin + endMax:
            - for querying imprecise positions (e.g. identifying all structural variants starting anywhere between `startMin` <-> `startMax`,
            and ending anywhere between `endMin` <-> `endMax`
            - single or double sided precise matches can be achieved by setting `startMin` = `startMax` OR `endMin` = `endMax`
    :type startMax: Integer
    :param startMax: Maximum start coordinate. See `startMin`.
    :type end: Integer
    :param end: Precise end coordinate. See `start`.
    :type endMin: Integer
    :param endMin: Minimum end coordinate. See `startMin`.
    :type endMax: Integer
    :param endMax: Maximum end coordinate. See `startMin`.
    :type referenceBases: String
    :param referenceBases: Reference bases for this variant (starting from `start`). Accepted values: [ACGT]* When querying for variants without specific base
     alterations (e.g. imprecise structural variants with separate variantType as well as startMin & endMin ... parameters), the use of a single "N" value is
     required. See the REF field in VCF 4.2 specification.
    :type alternateBases: String
    :param alternateBases: The bases that appear instead of the reference bases. Accepted values: [ACGT]* or N.
            Symbolic ALT alleles (DEL, INS, DUP, INV, CNV, DUP:TANDEM, DEL:ME, INS:ME) will be represented in `variantType`.
            See the ALT field in VCF 4.2 specification
            Either `alternateBases` OR `variantType` is REQUIRED
    :type variantType: String
    :param variantType: The `variantType` is used to denote e.g. structural variants.
            Either `alternateBases´ OR `variantType` is REQUIRED
    :type assemblyId: String
    :param assemblyId: Assembly identifier
    :type datasetIds: String
    :param datasetIds: Identifiers of data sets, as defined in `BeaconDataset`. In case assemblyId doesn't match requested dataset(s) error will be raised
    (400 Bad request). If this field is not specified, all datasets should be queried.
    :type includeDatasetResponses: String
    :param includeDatasetResponses: Indicator of whether responses for individual data sets (`datasetAlleleResponses`) should be included in the response
    (`BeaconAlleleResponse`) to this request or not. If null (not specified), the default value of NONE is assumed.
            Accepted values : ['ALL', 'HIT', 'MISS', 'NONE']
    :type error_: Object
    :param error_: Error object for the error handler.
    :type datasetAlleleResponses: Dict
    :return datasetAlleleResponses: Dict of the response.
    :type true_datasetAlleleResponses: Dict
    :return true_datasetAlleleResponses: Dict of those responses that give `exists` = True.
    :type false_datasetAlleleResponses: Dict
    :return false_datasetAlleleResponses: Dict of those responses that give `exists` = False.
    :type includeDatasetResponses: String
    :return includeDatasetResponses: The `includeDatasetResponses` from the request.
    """

    refname = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X', 'Y']
    datasetresponses = ['ALL', 'HIT', 'MISS', 'NONE']
    assembliIds = ['GRCh37', 'GRCh38', 'grch37', 'grch38']
    Bases = ['A', 'C', 'G', 'T', 'N', '0']  # The Zero is there to validate that it is missing
    variantTypes = ['DEL', 'INS', 'DUP', 'INV', 'CNV', 'SNP', 'DUP:TANDEM', 'DEL:ME', 'INS:ME']
    datasetAlleleResponses = []
    datasetIds_list = []
    Beacon = beacon_info.constructor()
    BeaconDataset = Beacon['dataset']
    for dset in BeaconDataset:
        datasetIds_list.append(dset['name'])

    pos = position(start, end, startMin, startMax, endMin, endMax)
    logging.debug(' * The position() function returned the array: {}'.format(pos))

    # check if referenceName parameter is missing
    if referenceName == '0':
        logging.warning(' * ERROR BAD REQUEST: Missing mandatory parameter referenceName')
        error_.bad_request('Missing mandatory parameter referenceName')
    # check if referenceName is valid
    elif referenceName not in refname:
        # if an error occures the 'exists' must be 'null'
        logging.warning(' * ERROR BAD REQUEST: referenceName not valid')
        for set in datasetAlleleResponses:
            set['exists'] = None
        error_.bad_request('referenceName not valid')

    # check if start/startMin parameter is missing
    if start == 0:
        if startMin == 0:
            logging.warning(' * ERROR BAD REQUEST: Missing mandatory parameter start or startMin')
            error_.bad_request('Missing mandatory parameter start or startMin')
    # check if the positional arguments are valid
    elif start < 0:
        logging.warning(' * ERROR BAD REQUEST: start not valid')
        error_.bad_request('start not valid')
    if startMin < 0:
        logging.warning(' * ERROR BAD REQUEST: startMin not valid')
        error_.bad_request('startMin not valid')
    if startMax < 0:
        logging.warning(' * ERROR BAD REQUEST: startMax not valid')
        error_.bad_request('startMax not valid')
    if endMin < 0:
        logging.warning(' * ERROR BAD REQUEST: endMin not valid')
        error_.bad_request('endMin not valid')
    if endMax < 0:
        logging.warning(' * ERROR BAD REQUEST: endMax not valid')
        error_.bad_request('endMax not valid')
    if end < 0:
        logging.warning(' * ERROR BAD REQUEST: end not valid')
        error_.bad_request('end not valid')

    # check if referenceBases parameter is missing
    if referenceBases == '0':
        logging.warning(' * ERROR BAD REQUEST: Missing mandatory parameter referenceBases')
        error_.bad_request('Missing mandatory parameter referenceBases')
    # check if the string items in the referenceBases are valid
    for nucleotide2 in referenceBases:
        if nucleotide2 not in Bases:
            logging.warning(' * ERROR BAD REQUEST: referenceBases not valid')
            error_.bad_request('referenceBases not valid')

    # check if alternateBases parameter is missing
    if alternateBases == '0':
        # if alternateBases is missing, check if variantType is missing
        if variantType == '0':
            logging.warning(' * ERROR BAD REQUEST: Missing mandatory parameter alternateBases or variantType')
            error_.bad_request('Missing mandatory parameter alternateBases or variantType')
        # check if variantType parameter is valid
        elif variantType not in variantTypes:
            logging.warning(' * ERROR BAD REQUEST: variantType not valid')
            error_.bad_request('variantType not valid')
    # check if the string items in the alternateBases are valid
    for nucleotide1 in alternateBases:
        if nucleotide1 not in Bases:
            logging.warning(' * ERROR BAD REQUEST: alternateBases not valid')
            error_.bad_request('alternateBases not valid')

    # check if assemblyId is missing
    if assemblyId == '0':
        logging.warning(' * ERROR BAD REQUEST: Missing mandatory parameter assemblyId')
        error_.bad_request('Missing mandatory parameter assemblyId')
    # check if assemblyId parameter is valid
    elif assemblyId not in assembliIds:
        logging.warning(' * ERROR BAD REQUEST: assemblyId not valid')
        error_.bad_request('assemblyId not valid')

    # check if includeDataserResponses is missing
    if includeDatasetResponses not in datasetresponses:
        # if an error occurs the 'exists' must be 'null'
        for set in datasetAlleleResponses:
            set['exists'] = None
        logging.warning(' * ERROR BAD REQUEST: includeDatasetResponses not valid')
        error_.bad_request('includeDatasetResponses not valid')

    # checks if there are datasetIds given. If there are, then check if the the datasetIds are in the database Table.
    # If not give ERROR. If they are correct, build a response for each data set that is correct.
    if datasetIds:
        for set in datasetIds:
            if set not in datasetIds_list:
                logging.warning(' * ERROR BAD REQUEST: datasetId not valid')
                error_.bad_request('datasetId not valid')
            logging.debug(' * Started building datasetAlleleResponse for: {}'.format(set))
            datasetAlleleResponses.append(datasetAlleleResponseBuilder(set, referenceName, pos, alternateBases, variantType, BeaconDataset))
            logging.debug(' * Finnished building datasetAlleleResponse for: {}'.format(set))
    # if no data sets where given, it will query all data sets in the database
    else:
        datasetIds = datasetIds_list
        for set in datasetIds:
            logging.debug(' * Started building datasetAlleleResponse for: {}'.format(set))
            datasetAlleleResponses.append(datasetAlleleResponseBuilder(set, referenceName, pos, alternateBases, variantType, BeaconDataset))
            logging.debug(' * Finnished building datasetAlleleResponse for: {}'.format(set))

    # creates empty lists for specific datasetResponses
    false_datasetAlleleResponses = []
    true_datasetAlleleResponses = []
    # fills the lists with the responses
    for response in datasetAlleleResponses:
        if not response['exists']:
            false_datasetAlleleResponses.append(response)
        elif response['exists']:
            true_datasetAlleleResponses.append(response)

    return datasetAlleleResponses, true_datasetAlleleResponses, false_datasetAlleleResponses, includeDatasetResponses


def checkifdatasetisTrue(datasets):
    """
    The `checkifdatasetisTrue()` function checks the individual data sets and returns True if any of the data sets have exists == True.

    :type datasets: Dict
    :param datasets: Dict of the response from the data set.
    :return: boolean
    """
    for value in datasets:
        if value['exists']:
            return True
    return False


def checkInclude(includeDatasetResponses, alldatasets, trurdatasets, falsedatasets):
    """
    The function returns those data set responses that the `includeDatasetResponses` parameter decides.

    :type includeDatasetResponses: String
    :param includeDatasetResponses: The `includeDatasetResponses` from the request.
    :type alldatasets: Dict
    :param alldatasets: Dicts of all the responses.
    :type trurdatasets: Dict
    :param trurdatasets: Dicts of all the data sets that have `exists` = True.
    :type falsedatasets: Dict
    :param falsedatasets: Dicts of all the data sets that have `exists` = False.
    :type alldatasets: Dict
    :return alldatasets: Dicts of all the responses.
    :type trurdatasets: Dict
    :return trurdatasets: Dicts of all the data sets that have `exists` = True.
    :type falsedatasets: Dict
    :return falsedatasets: Dicts of all the data sets that have `exists` = False.
    """
    if includeDatasetResponses == 'ALL':
        return alldatasets
    elif includeDatasetResponses == 'NONE':
        return []
    elif includeDatasetResponses == 'HIT':
        return trurdatasets
    elif includeDatasetResponses == 'MISS':
        return falsedatasets

from beacon_api.beacon_database import *
import sqlite3,time




#Some hard coded data for the querys, some are taken from the beacon_dicts.py
#These will be implemented later to thake the data from a database
refname = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11','12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X', 'Y']
datasetresponses = ['ALL', 'HIT', 'MISS', 'NONE']
assembliIds = ['GRCh37', 'GRCh38', 'grch37', 'grch38']
Bases = ['A', 'C', 'G', 'T', 'N', '0'] # The Zero is there to validate thet it is missing
variantTypes = ['DEL', 'INS', 'DUP', 'INV', 'CNV', 'SNP', 'DUP:TANDEM', 'DEL:ME', 'INS:ME']
Beacon = constructor()
BeaconDataset = Beacon['dataset']
datasetIds_list = []
for dset in BeaconDataset:
    datasetIds_list.append(dset['name'])


'''The `position()` function checks the values of the position parameters (start, startMin, startMax, end, endMain, endMax)
and returns a positon list `pos` that depending on the submitted parameters, either have one, two or four items.
'''

def position(start, end, startMin, startMax, endMin, endMax):
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
    # fuzzy bounderies
    if startMin != 0 and startMax != 0 and endMin != 0 and endMax != 0:
        pos.append(startMin)
        pos.append(startMax)
        pos.append(endMin)
        pos.append(endMax)
        return pos

'''The `allelFind()` function queries the database with the submitted parameters and checks if it finds the allele in the right place.
It returns `True` if found and `False`if not. It also returns the object to the row that was queried in the database.'''

def allelFind(chromosome, position, allel=None, variantType=None):
    # if alternateBases or variantType are not defined they are set to None
    eka = time.time()
    conn = sqlite3.connect('/Users/kakeinan/beacon-python/beacon_api/beaconDatabase.db')
    c = conn.cursor()

    if variantType != None:
        if len(position) == 1:
            c.execute('SELECT * FROM genomes WHERE chromosome=? AND start=? AND  type=?',(chromosome, position[0], variantType))

        elif len(position) == 2:
            c.execute('SELECT * FROM genomes WHERE chromosome=? AND start=? AND end=? AND type=?',(chromosome, position[0], position[1] , variantType))

        else:
            c.execute('SELECT * FROM genomes WHERE chromosome=? AND start>=? AND start<=? AND end>=? AND end<=? AND type=?',(chromosome, position[0], position[1], position[2], position[3], variantType))

    elif variantType == None:
        if len(position) == 1:
            c.execute('SELECT * FROM genomes WHERE chromosome=? AND start=? AND  alternate=?',
                      (chromosome, position[0], allel))

        elif len(position) == 2:
            c.execute('SELECT * FROM genomes WHERE chromosome=? AND start=? AND end=? AND alternate=?',
                      (chromosome, position[0], position[1], allel))
        else:
            c.execute(
                'SELECT * FROM genomes WHERE chromosome=? AND start>=? AND start<=? AND end>=? AND end<=? AND alternate=?',
                (chromosome, position[0], position[1], position[2], position[3], allel))

    print("sql haku: {}".format(time.time()-eka))
    row = c.fetchone()
    conn.close()

    if row == None:
        return False, row
    else:
        return True, row

#
#    q_obj = Beacon_data_table
#    q_obj_chrm = q_obj.query.filter_by(chromosome=chromosome).all()#list
#
#    if not q_obj_chrm:
#        return None, q_obj.query.filter_by(chromosome=1).all()[0] # expecting that there will allways be chromosome 1 and just returns it as dummy
#
#    for q_chrom in q_obj_chrm:
#        # only start
#        if len(position) == 1:
#            if q_chrom.start == position[0]:
#                if q_chrom.alternate == allel:
#                    print("SQLAlchemy haku: {}".format(time.time() - toka))
#
#                    return True, q_chrom
#        # start --> end
#        elif len(position) == 2:
#            if q_chrom.start == position[0] and q_chrom.end == position[1]:
#                if q_chrom.alternate == allel:
#                    return True, q_chrom
#        # startMin ... startMax --> endMin .. endMax
#        elif len(position) == 4:
#            startRange = range(position[0], position[1]+1)
#            endRange = range(position[2], position[3]+1)
#            if q_chrom.start in startRange and q_chrom.end in endRange:
#                if q_chrom.alternate == allel:
#                    return True, q_chrom
#
#
#    return False, q_chrom

'''The `datasetAllelResponseBuilder()` function calls the `allelFind()` function and receives the answer to the exist parameter
and the database object to the row in the database. If `exists == False` the function sets the variant_cnt, sample_cnt,
call_cnt and frequensy to 0. And if `exists == True` the function gets the parameter values from the database.'''

def datasetAllelResponseBuilder(datasetId, referencename, pos, alternateBases, variantType):
    error = None
    j = 0
    for i in BeaconDataset:
        if datasetId in i['name']:
            break
        j += 1

    exists, row = allelFind(referencename, pos, alternateBases, variantType)

    if exists == False:
        variantCount, sampleCount, callCount, frequency = 0,0,0,0 # does not alter the database only the representation
    else:
        frequency = row[12]
        sampleCount = row[11]
        callCount = row[10]
        variantCount = row[9]

    datasetAllelResponse = {
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
    return datasetAllelResponse

'''The `checkParameters()` function valiates the submitted parameters values and checks if required parameters are missing.
It calls the appropriate BeaconError method if something is wrong.'''

def checkParameters(referenceName, start, startMin, startMax, end, endMin, endMax, \
                    referenceBases, alternateBases, variantType,assemblyId, datasetIds, includeDatasetResponses, error_):
    datasetAllelResponses = []

    pos = position(start, end, startMin, startMax, endMin, endMax)



    # check if referenceName parameter is missing
    if referenceName == '0':
        error_.bad_request('Missing mandatory parameter referenceName')
    # check if referenceName is valid
    elif referenceName not in refname:
        #if an error occures the 'exists' must be 'null'
        for set in datasetAllelResponses:
            set['exists'] = None
        error_.bad_request('referenceName not valid')



    # check if start/startMin parameter is missing
    if start == 0:
        if startMin == 0:
            error_.bad_request('Missing mandatory parameter start or startMin')
    # check if the positional arguments are valid
    elif start < 0:
        error_.bad_request('start not valid')
    if startMin < 0:
        error_.bad_request('startMin not valid')
    if startMax < 0:
        error_.bad_request('startMin not valid')
    if endMin < 0:
        error_.bad_request('endMin not valid')
    if endMax < 0:
        error_.bad_request('endMax not valid')
    if end < 0:
        error_.bad_request('end not valid')



    # check if referenceBases parameter is missing
    if referenceBases == '0':
        error_.bad_request('Missing mandatory parameter referenceBases')
    # check if the string items in the referenceBases are valid
    for nucleotide2 in referenceBases:
        if nucleotide2 not in Bases:
            error_.bad_request('referenceBases not valid')



    # check if alternateBases parameter is missing
    if alternateBases == '0':
        # if alternateBases is missing, check if variantType is missing
        if variantType == '0':
            error_.bad_request('Missing mandatory parameter alternateBases or variantType')
        # check if variantType parameter is valid
        elif variantType not in variantTypes:
            error_.bad_request('variantType not valid')
    # check if the string items in the alternateBases are valid
    for nucleotide1 in alternateBases:
        if nucleotide1 not in Bases:
            error_.bad_request('alternateBases not valid')


    # check if assemblyId is missing
    if assemblyId == '0':
        error_.bad_request('Missing mandatory parameter assemblyId')
    # check if assemblyId parameter is valid
    elif assemblyId not in assembliIds:
        error_.bad_request('assemblyId not valid')



    # check if includeDataserResponses is missing
    if includeDatasetResponses not in datasetresponses:
        # if an error occures the 'exists' must be 'null'
        for set in datasetAllelResponses:
            set['exists'] = None
        error_.bad_request('includeDatasetResponses not valid')


    # checks if there are datasetIds given. If there are, then check if the the datasetIds are in the database Table.
    # If not give ERROR. If they are correct, build a response for each dataset that is correct.
    if datasetIds:
        for set in datasetIds:
            if set not in datasetIds_list:
                error_.bad_request('datasetId not valid')
            datasetAllelResponses.append(datasetAllelResponseBuilder(set, referenceName, pos, alternateBases, variantType))
    # if no datasets where given, it will query all datasets in the database
    else:
        datasetIds = datasetIds_list
        for set in datasetIds:
            datasetAllelResponses.append(datasetAllelResponseBuilder(set, referenceName, pos, alternateBases, variantType))




    # creates empty lists for specific datasetResponses
    false_datasetAllelResponses = []
    true_datasetAllelResponses = []
    # fills the lists with the responses
    for response in datasetAllelResponses:
        if response['exists'] == False:
            false_datasetAllelResponses.append(response)
        elif response['exists'] == True:
            true_datasetAllelResponses.append(response)



    return datasetAllelResponses, true_datasetAllelResponses, false_datasetAllelResponses, includeDatasetResponses

'''The `checkifdatasetisTrue()` function checks the individual datasets and returns `True` if any of the datasets have 
`exists == True`.'''
# function checks if there are any True in the datasetResponses, if there is it will give a Tru for the whole response
def checkifdatasetisTrue(datasets):
    for value in datasets:
        if value['exists'] == True:
            return True
    return False

# the function returns those datasetresponses that the includeDatasetResponses parameter decides
def checkInclude(includeDatasetResponses, alldatasets, trurdatasets, falsedatasets):
    if includeDatasetResponses == 'ALL':
        return alldatasets
    elif includeDatasetResponses == 'NONE':
        return []
    elif includeDatasetResponses == 'HIT':
        return trurdatasets
    elif includeDatasetResponses == 'MISS':
        return falsedatasets
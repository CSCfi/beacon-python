from beacon_api.beacon_dicts import BeaconDataset
from beacon_api.beacon_database import *


#Some hard coded data for the querys, some are taken from the beacon_dicts.py
#These will be implemented later to thake the data from a database
refname = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11','12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X', 'Y']
datasetIds_list = []
for set in BeaconDataset:
    datasetIds_list.append(set['id'])
datasetresponses = ['ALL', 'HIT', 'MISS', 'NONE']


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

def allelFind(chromosome, position, allel, error_):
    q_obj = Beacon_data_table
    q_obj_chrm = q_obj.query.filter_by(chromosome=chromosome).all()   #list
    if not q_obj_chrm:
        error_.bad_request('Chromosome maching referenceName={}, not found in dataset'.format(chromosome))
    for q_chrom in q_obj_chrm:
        # only start
        if len(position) == 1:
            if q_chrom.start == position[0]:
                if q_chrom.alternate == allel:
                    return True, q_chrom
        # start --> end
        elif len(position) == 2:
            if q_chrom.start == position[0] and q_chrom.end == position[1]:
                if q_chrom.alternate == allel:
                    return True, q_chrom
        # startMin ... startMax --> endMin .. endMax
        elif len(position) == 4:
            startRange = range(position[0], position[1]+1)
            endRange = range(position[2], position[3]+1)
            if q_chrom.start in startRange and q_chrom.end in endRange:
                if q_chrom.alternate == allel:
                    return True, q_chrom


    return False, q_chrom


#The datasetAllelResponseBuilder() function takes in the datasetIds and creates individual responses
#for them which it puts in the datasetAllelResponses list, and returns it.
def datasetAllelResponseBuilder(datasetId, referencename, pos, alternateBases, error_):
    j = 0
    for i in BeaconDataset:
        if datasetId in i['id']:
            break
        j += 1
    exists, queryRow = allelFind(referencename, pos, alternateBases, error_)

    if exists == False:
        queryRow.variant_cnt, queryRow.sample_cnt, queryRow.call_cnt, queryRow.frequency = 0,0,0,0 # does not alter the database only the representation
    datasetAllelResponses = {
        'datasetId': datasetId,
        'exists': exists,
        'frequency': queryRow.frequency,
        'variantCount': queryRow.variant_cnt,
        'callCount': queryRow.call_cnt,
        'sampleCount': queryRow.sample_cnt,
        'note': BeaconDataset[j]['description'],
        'externalUrl': BeaconDataset[j]['externalUrl'],
        'info': BeaconDataset[j]['info'],
        'error': None
    }
    return datasetAllelResponses


#The checkParameters() function checks if there is anything wrong with the query parameters that
#the get or post recives. if there is something wrong it calls the appropriate error function (Now bad_request())
def checkParameters(referenceName, start, startMin, startMax, end, endMin, endMax, \
                    referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses, error_):
    datasetAllelResponses = []

    pos = position(start, end, startMin, startMax, endMin, endMax)

    if referenceName == '0' or start == 0 or referenceBases == '0' or alternateBases == '0' or assemblyId == '0':

        #if an error occures the 'exists' must be 'null'
        for set in datasetAllelResponses:
            set['exists'] = None
        if referenceName == '0':
            error_.bad_request('Missing manadory parameter referenceName')
        if start == 0:
            if startMin == 0:
                error_.bad_request('Missing manadory parameter start or startMin')

        if referenceBases == '0':
            error_.bad_request('Missing manadory parameter referenceBases')
        if alternateBases == '0':
            error_.bad_request('Missing manadory parameter alternateBases')
        if assemblyId == '0':
            error_.bad_request('Missing manadory parameter assemblyId')

        

    if referenceName not in refname or includeDatasetResponses not in datasetresponses:
        #if an error occures the 'exists' must be 'null'
        for set in datasetAllelResponses:
            set['exists'] = None
        error_.bad_request('Referencename or includeDatasetResponses not valid')



    if datasetIds:
        for set in datasetIds:
            if set not in datasetIds_list:
                error_.bad_request(datasetAllelResponses)
            datasetAllelResponses.append(datasetAllelResponseBuilder(set, referenceName, pos, alternateBases, error_))
    else:
        datasetIds = None
        datasetAllelResponses = None





    if includeDatasetResponses == 'NONE':
        datasetAllelResponses = None

    return datasetAllelResponses, includeDatasetResponses

# Determines the 'exists' in the beacon query by checking the dataset querys
def checkifdatasetisTrue(datasets):
    for value in datasets:
        if value['exists'] == True:
            return True
    return False

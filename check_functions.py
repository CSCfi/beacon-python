from beacon_dicts import BeaconDataset
from error_handelers import *


#Some hard coded data for the querys, some are taken from the beacon_dicts.py
#These will be implemented later to thake the data from a database
refname = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11','12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X', 'Y']
start_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
refbases = ['A', 'C', 'G', 'T', 'N']
assembly_list =['GRCh37', 'GRCh38']
datasetIds_list = []
for set in BeaconDataset:
    datasetIds_list.append(set['id'])
datasetresponses = ['ALL', 'HIT', 'MISS', 'NONE']

def position():
    pass

def allelFind():

    return False

#The datasetAllelResponseBuilder() function takes in the datasetIds and creates individual responses
#for them which it puts in the datasetAllelResponses list, and returns it.
def datasetAllelResponseBuilder(datasetId):
    j = 0
    for i in BeaconDataset:
        if datasetId in i['id']:
            break
        j += 1

    datasetAllelResponses = {
        'datasetId': datasetId,
        'exists': allelFind(),
        'frequency': 0,
        'variantCount': BeaconDataset[j]['variantCount'],
        'callCount': BeaconDataset[j]['callCount'],
        'sampleCount': BeaconDataset[j]['sampleCount'],
        'note': BeaconDataset[j]['description'],
        'externalUrl': BeaconDataset[j]['externalUrl'],
        'info': BeaconDataset[j]['info'],
        'error': None
    }
    return datasetAllelResponses


#The checkParameters() function checks if there is anything wrong with the query parameters that
#the get or post recives. if there is something wrong it calls the appropriate error function (Now bad_request())
def checkParameters(referenceName, start, startMin, startMax, end, endMin, endMax, \
                    referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses):
    datasetAllelResponses = []

    if datasetIds:
        for set in datasetIds:
            if set not in datasetIds_list:
                bad_request(referenceName, start, startMin, startMax, end, endMin, endMax, \
                            referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses, datasetAllelResponses)
            datasetAllelResponses.append(datasetAllelResponseBuilder(set))
    else:
        datasetIds = None
        datasetAllelResponses = None

    if referenceName == '0' or start == 0 or referenceBases == '0' or alternateBases == '0' or assemblyId == '0':
        #if an error occures the 'exists' must be 'null'
        for set in datasetAllelResponses:
            set['exists'] = None
        bad_request(referenceName, start, startMin, startMax, end, endMin, endMax, \
                    referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses, datasetAllelResponses)

    if referenceName not in refname or start not in start_list or referenceBases not in refbases or assemblyId not in assembly_list or includeDatasetResponses not in datasetresponses:
        #if an error occures the 'exists' must be 'null'
        for set in datasetAllelResponses:
            set['exists'] = None
        bad_request(referenceName, start, startMin, startMax, end, endMin, endMax, \
                    referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses, datasetAllelResponses)

    if includeDatasetResponses == 'NONE':
        datasetAllelResponses = None

    return datasetAllelResponses, includeDatasetResponses

# Determines the 'exists' in the beacon query by checking the dataset querys
def checkifdatasetisTrue(datasets):
    for value in datasets:
        if value['exists'] == True:
            return True
    return False

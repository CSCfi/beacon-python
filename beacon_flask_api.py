from flask import Flask, jsonify
from flask_restful import Api, Resource
from beacon_dicts import BeaconDataset
from webargs import fields
from webargs.flaskparser import use_kwargs
from error_handelers import *


app = Flask(__name__)
api = Api(app)

#Some hard coded data for the querys, some are taken from the beacon_dicts.py
#These will be implemented later to thake the data from a database
apiVersion = Beacon['apiVersion']
beaconId = Beacon['id']
refname = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11','12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X', 'Y']
start_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
refbases = ['A', 'C', 'G', 'T', 'N']
assembly_list =['GRCh37', 'GRCh38']
datasetIds_list = []
for set in BeaconDataset:
    datasetIds_list.append(set['id'])
datasetresponses = ['ALL', 'HIT', 'MISS', 'NONE']


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
        'exists': False,
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


# '/' Get gives basic info on the api
class Beacon_get(Resource):
    def get(self):
        return jsonify(Beacon)#Not the same order as in example

api.add_resource(Beacon_get,'/')

# '/query' Get/Post responds with the answer: 'exists': True/False  and the given parameters if the parameters are valid
class Beacon_query(Resource):
    args = {
        'referenceName': fields.Str(
            missing='0'
        ),
        'start': fields.Int(
            missing=0
        ),
        'startMin': fields.Int(
            missing=0
        ),
        'startMax': fields.Int(
            missing=0
        ),
        'end': fields.Int(
            missing=0
        ),
        'endMin': fields.Int(
            missing=0
        ),
        'endMax': fields.Int(
            missing=0
        ),
        'referenceBases': fields.Str(
            missing='0'
        ),
        'alternateBases': fields.Str(
            missing='0'
        ),
        'assemblyId': fields.Str(
            missing='0'
        ),
        'datasetIds': fields.List(fields.Str(
            missing=None
        )),
        'includeDatasetResponses': fields.Str(
            missing='ALL',
        ),
    }

    @use_kwargs(args)
    def get(self, referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses):

        datasetAllelResponses, includeDatasetResponses = checkParameters(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses)

        allelRequest = {'referenceName': referenceName,
                        'start': start,
                        'startMin': startMin,
                        'startMax': startMax,
                        'end': end,
                        'endMin': endMin,
                        'endMax': endMax,
                        'referenceBases': referenceBases,
                        'alternateBases': alternateBases,
                        'assemblyId': assemblyId,
                        'datasetIds': datasetIds,
                        'includeDatasetResponses': includeDatasetResponses,
                        }

        return {'beaconId': beaconId,
                "apiVersion": apiVersion,
                'exists': checkifdatasetisTrue(datasetAllelResponses),
                'error': None,
                'allelRequest': allelRequest,
                'datasetAllelResponses': datasetAllelResponses}

    @use_kwargs(args)
    def post(self, referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, assemblyId, datasetIds , includeDatasetResponses):

        datasetAllelResponses, includeDatasetResponses = checkParameters(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses)

        allelRequest = {'referenceName': referenceName,
                        'start': start,
                        'startMin': startMin,
                        'startMax': startMax,
                        'end': end,
                        'endMin': endMin,
                        'endMax': endMax,
                        'referenceBases': referenceBases,
                        'alternateBases': alternateBases,
                        'assemblyId': assemblyId,
                        'datasetIds': datasetIds,
                        'includeDatasetResponses': includeDatasetResponses,
                        }

        return {"beaconId": beaconId,
                "apiVersion": apiVersion,
                "exists": False,
                "error": None,
                "alleleRequest": allelRequest,
                "datasetAlleleResponses": datasetAllelResponses}

api.add_resource(Beacon_query,'/query')

if __name__ == '__main__':
    app.run(debug=True)
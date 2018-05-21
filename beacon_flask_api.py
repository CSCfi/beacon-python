from flask import Flask, jsonify
from flask_restful import Api, Resource
from beacon_dicts import BeaconDataset
from webargs import fields
from webargs.flaskparser import use_kwargs

from check_functions import *


app = Flask(__name__)
api = Api(app)


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

        return {'beaconId': Beacon['id'],
                "apiVersion": Beacon['apiVersion'],
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

        return {"beaconId": Beacon['id'],
                "apiVersion": Beacon['apiVersion'],
                "exists": checkifdatasetisTrue(datasetAllelResponses),
                "error": None,
                "alleleRequest": allelRequest,
                "datasetAlleleResponses": datasetAllelResponses}

api.add_resource(Beacon_query,'/query')

if __name__ == '__main__':
    app.run(debug=True)
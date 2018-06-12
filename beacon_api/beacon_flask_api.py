from flask import jsonify
from flask_restful import Api, Resource
from webargs import fields
from webargs.flaskparser import use_kwargs

from beacon_api.check_functions import *
from beacon_api.error_handelers import BeaconError
from beacon_api.beacon_database import app



api = Api(app)
Beacon = constructor()

class Beacon_get(Resource):
    '''The `get()` method in the Beacon_get class uses the HTTP protocol 'GET' to returns a Json object of all the nessesary info on the beacon and the Api. It
    uses the '/' path and only serves an information giver. The parameters that the method returns and their descriptions
    can be found under the title: Beacon'''''
    def get(self):
        return jsonify(Beacon)

api.add_resource(Beacon_get,'/')

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

    '''The `get()` method of the Beacon_query class gets it's parameters from the `@use_kwargs(args)` decorator and uses the HTTP
    protocol 'GET' to return a Json object. The object contains the `alleleRequest` that was submitted, the `datasetAlleleResponse`
    that was received, some general info on the api and the parameter `exists`. The `exists` parameter is the answer from the
    query that tells the user if the allele was found or not.
    ###
    But first the methods creates the BeaconError object `error_` so it can use it's error handlers. Then it checks that the
    submitted parameters are valid and gets the `datasetAllelResponses` and the `includeDatasetResponses` from the 
    `checkParameters()` method.'''

    @use_kwargs(args)
    def get(self, referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses):

        error_ = BeaconError(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses)
        datasetAllelResponses, includeDatasetResponses = checkParameters(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses, error_)

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

    '''The `post()` method runs the same code as the `get()` method but uses the HTTP protocol `POST` instead. The main difference
    between the methods is that the parameters are not sent in the URL. This is more secure because the `GET` requests URLs get
    logged and then if you use the `POST` instead, you dont reveal the parameters that you query with.'''

    @use_kwargs(args)
    def post(self, referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, assemblyId, datasetIds , includeDatasetResponses):


        error_ = BeaconError(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases,
                             alternateBases, assemblyId, datasetIds, includeDatasetResponses)

        datasetAllelResponses, includeDatasetResponses = checkParameters(referenceName, start, startMin, startMax, end,
                                                                         endMin, endMax, referenceBases, alternateBases,
                                                                         assemblyId, datasetIds,
                                                                         includeDatasetResponses, error_)

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
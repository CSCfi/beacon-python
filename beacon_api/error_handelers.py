from flask import abort

apiVersion = "0.4"
beaconId = "ega-beacon"
class BeaconError():
    def __init__(self, referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId, datasetIds, includeDatasetResponses):
        self.referenceName = referenceName
        self.start = start
        self.startMin = startMin
        self.startMax = startMax
        self.end = end
        self.endMin = endMin
        self.endMax = endMax
        self.referenceBases = referenceBases
        self.alternateBases = alternateBases
        self.variantTYpe = variantType
        self.assemblyId = assemblyId
        self.datasetIds = datasetIds
        self.includeDatasetResponses = includeDatasetResponses

    '''The `bad_request()` method aborts the actions of the api and returns a 400 error code and a customised error message. 
    The method is called if one of the required parameters are missing or invalid.'''

    def bad_request(self, message):
        abort(400, {'beaconId': beaconId,
                    "apiVersion": apiVersion,
                    'exists': None,
                    'error': {
                        'errorCode': 400,
                        'errorMessage': message #'Bad request, missing mandatory parameter or the value is not valid!'
                    },
                    'allelRequest': {'referenceName': self.referenceName,
                                     'start': self.start,
                                     'startMin': self.startMin,
                                     'startMax': self.startMax,
                                     'end': self.end,
                                     'endMin': self.endMin,
                                     'endMax': self.endMax,
                                     'referenceBases': self.referenceBases,
                                     'alternateBases': self.alternateBases,
                                     'variantType': self.variantTYpe,
                                     'assemblyId': self.assemblyId,
                                     'datasetIds': self.datasetIds,
                                     'includeDatasetResponses': self.includeDatasetResponses,
                                     },
                    'datasetAllelResponses': []}
              )

    '''The `unauthorised()` method aborts the actions of the api and returns a 401 error code with the error message 
    `'Unauthenticated user trying to access protected resource.'`. The method is called if the user does'nt have access 
    '''

    def unauthorised(self, message):
        abort(401, {'beaconId': beaconId,
                    "apiVersion": apiVersion,
                    'exists': None,
                    'error': {
                        'errorCode': 401,
                        'errorMessage': message
                    },
                    'allelRequest': {'referenceName': self.referenceName,
                                     'start': self.start,
                                     'startMin': self.startMin,
                                     'startMax': self.startMax,
                                     'end': self.end,
                                     'endMin': self.endMin,
                                     'endMax': self.endMax,
                                     'referenceBases': self.referenceBases,
                                     'alternateBases': self.alternateBases,
                                     'variantType': self.variantTYpe,
                                     'assemblyId': self.assemblyId,
                                     'datasetIds': self.datasetIds,
                                     'includeDatasetResponses': self.includeDatasetResponses,
                                     },
                    'datasetAllelResponses': []}
              )

    '''The `forbidden()` method method aborts the actions of the api and returns a 403 error code with the error message 
    `'Resource not granted for authenticated user or resource protected for all users.'`. The method is called if the dataset
    is protected or if the user is authenticated but not granted the resource.
    '''

    def forbidden(self):
        abort(403, {'beaconId': beaconId,
                    "apiVersion": apiVersion,
                    'exists': None,
                    'error': {
                        'errorCode': 403,
                        'errorMessage': 'Resource not granted for authenticated user or resource protected for all users.'
                    },
                    'allelRequest': {'referenceName': self.referenceName,
                                     'start': self.start,
                                     'startMin': self.startMin,
                                     'startMax': self.startMax,
                                     'end': self.end,
                                     'endMin': self.endMin,
                                     'endMax': self.endMax,
                                     'referenceBases': self.referenceBases,
                                     'alternateBases': self.alternateBases,
                                     'variantType': self.variantTYpe,
                                     'assemblyId': self.assemblyId,
                                     'datasetIds': self.datasetIds,
                                     'includeDatasetResponses': self.includeDatasetResponses,
                                     },
                    'datasetAllelResponses': []}
              )


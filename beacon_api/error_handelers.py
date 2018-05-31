from flask import abort
from beacon_api.beacon_dicts import Beacon

apiVersion = Beacon['apiVersion']
beaconId = Beacon['id']
class BeaconError():
    def __init__(self, referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses):
        self.referenceName = referenceName
        self.start = start
        self.startMin = startMin
        self.startMax = startMax
        self.end = end
        self.endMin = endMin
        self.endMax = endMax
        self.referenceBases = referenceBases
        self.alternateBases = alternateBases
        self.assemblyId = assemblyId
        self.datasetIds = datasetIds
        self.includeDatasetResponses = includeDatasetResponses


    #The bad_request() function returns a 400 code along with the parameters and a errormessage
    #The function is used if there are missing mandatory parameters or if they are in the wrong format/not valid
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
                                     'assemblyId': self.assemblyId,
                                     'datasetIds': self.datasetIds,
                                     'includeDatasetResponses': self.includeDatasetResponses,
                                     },
                    'datasetAllelResponses': []}
              )
    def unauthorised(self, datasetAllelResponses):
        abort(401, {'beaconId': beaconId,
                    "apiVersion": apiVersion,
                    'exists': None,
                    'error': {
                        'errorCode': 401,
                        'errorMessage': 'Unauthenticated user trying to acces protected resource.'
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
                                     'assemblyId': self.assemblyId,
                                     'datasetIds': self.datasetIds,
                                     'includeDatasetResponses': self.includeDatasetResponses,
                                     },
                    'datasetAllelResponses': datasetAllelResponses}
              )

    def forbidden(self, datasetAllelResponses):
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
                                     'assemblyId': self.assemblyId,
                                     'datasetIds': self.datasetIds,
                                     'includeDatasetResponses': self.includeDatasetResponses,
                                     },
                    'datasetAllelResponses': datasetAllelResponses}
              )
from flask import abort
from beacon_dicts import Beacon


apiVersion = Beacon['apiVersion']
beaconId = Beacon['id']
#The bad_request() function returns a 400 code along with the parameters and a errormessage
#The function is used if there are missing mandatory parameters or if they are in the wrong format/not valid
def bad_request(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses, datasetAllelResponses):
    abort(400, {'beaconId': beaconId,
                "apiVersion": apiVersion,
                'exists': None,
                'error': {
                    'errorCode': 400,
                    'errorMessage': 'Bad request, missing mandatory parameter or the value is not valid!'
                },
                'allelRequest': {'referenceName': referenceName,
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
                                 },
                'datasetAllelResponses': datasetAllelResponses}
          )
def unauthorised(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses, datasetAllelResponses):
    abort(401, {'beaconId': beaconId,
                "apiVersion": apiVersion,
                'exists': None,
                'error': {
                    'errorCode': 401,
                    'errorMessage': 'Unauthenticated user trying to acces protected resource.'
                },
                'allelRequest': {'referenceName': referenceName,
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
                                 },
                'datasetAllelResponses': datasetAllelResponses}
          )

def forbidden(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses, datasetAllelResponses):
    abort(403, {'beaconId': beaconId,
                "apiVersion": apiVersion,
                'exists': None,
                'error': {
                    'errorCode': 403,
                    'errorMessage': 'Resource not granted for authenticated user or resource protected for all users.'
                },
                'allelRequest': {'referenceName': referenceName,
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
                                 },
                'datasetAllelResponses': datasetAllelResponses}
          )
import json
from aiohttp import web
from .. import __apiVersion__


class BeaconError(Exception):
    """BeaconError Exception specifc class.

    Generates custom exception messages based on request parameters.
    """

    def __init__(self, request, error_code, error):
        """Return request data as dictionary."""
        self.data = {'beaconId': '.'.join(reversed(request.host.split('.'))),
                     "apiVersion": __apiVersion__,
                     'exists': None,
                     'error': {
                        'errorCode': error_code,
                        'errorMessage': error  # 'Bad request, missing mandatory parameter or the value is not valid!'
                     },
                     'allelRequest': {'referenceName': request["referenceName"],
                                      'start': request["start"],
                                      'startMin': request["startMin"],
                                      'startMax': request["startMax"],
                                      'end': request["end"],
                                      'endMin': request["endMin"],
                                      'endMax': request["endMax"],
                                      'referenceBases': request["referenceBases"],
                                      'alternateBases': request["alternateBases"],
                                      'variantType': request["variantType"],
                                      'assemblyId': request["assemblyId"],
                                      'datasetIds': request["datasetIds"],
                                      'includeDatasetResponses': request["includeDatasetResponses"], },
                     'datasetAllelResponses': []}
        return self.data


class BeaconBadRequest(BeaconError):
    """Raise an HTTP Exception returns with 400 code and a customised error message.

    The method is called if one of the required parameters are missing or invalid.
    Used in conjuction with JSON Schema validator.
    """

    def __init__(self, request, error):
        """Return custom bad request exception."""
        data = super().__init__(request, 400, error)

        raise web.HTTPBadRequest(content_type="application/json", body=json.dumps(data).encode('utf-8'))


class BeaconUnauthorised(BeaconError):
    """Raise an HTTP Exception returns with 401 code with a custom error message.

    The method is called if the user is not registered or if the token from the authentication has expired.
    Used in conjuction with Token authentication aiohttp middleware.
    """

    def __init__(self, request, error):
        """Return custom unauthorized exception."""
        data = super().__init__(request, 401, error)

        raise web.HTTPUnauthorized(content_type="application/json", body=json.dumps(data).encode('utf-8'))


class BeaconForbidden(BeaconError):
    """Raise an HTTP Exception returns with 403 code with the error message.

    `'Resource not granted for authenticated user or resource protected for all users.'`. The method is called if the dataset
    is protected or if the user is authenticated but not granted the resource.
    Used in conjuction with Token authentication aiohttp middleware.
    """

    def __init__(self, request, error):
        """Return custom forbidden exception."""
        data = super().__init__(request, 403, error)

        raise web.HTTPUnauthorized(content_type="application/json", body=json.dumps(data).encode('utf-8'))

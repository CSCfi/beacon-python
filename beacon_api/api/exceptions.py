import json
from aiohttp import web
from .. import __apiVersion__
from ..utils.logging import LOG


class BeaconError(Exception):
    """BeaconError Exception specifc class.

    Generates custom exception messages based on request parameters.
    """

    def __init__(self, request, host, error_code, error):
        """Return request data as dictionary."""
        self.data = {'beaconId': '.'.join(reversed(host.split('.'))),
                     "apiVersion": __apiVersion__,
                     'exists': None,
                     'error': {
                        'errorCode': error_code,
                        'errorMessage': error  # 'Bad request, missing mandatory parameter or the value is not valid!'
                     },
                     'allelRequest': {'referenceName': request.get("referenceName", 1),
                                      'start': request.get("start", 0),
                                      'startMin': request.get("startMin", 0),
                                      'startMax': request.get("startMax", 0),
                                      'end': request.get("end", 0),
                                      'endMin': request.get("endMin", 0),
                                      'endMax': request.get("endMax", 0),
                                      'referenceBases': request.get("referenceBases"),
                                      'alternateBases': request.get("alternateBases", "N"),
                                      'variantType': request.get("variantType", "0"),
                                      'assemblyId': request.get("assemblyId", 0),
                                      'datasetIds': request.get("datasetIds", []),
                                      'includeDatasetResponses': request.get("includeDatasetResponses", []), },
                     'datasetAllelResponses': []}
        # TO DO add variant + alternateBases logic
        return self.data


class BeaconBadRequest(BeaconError):
    """Raise an HTTP Exception returns with 400 code and a customised error message.

    The method is called if one of the required parameters are missing or invalid.
    Used in conjuction with JSON Schema validator.
    """

    def __init__(self, request, host, error):
        """Return custom bad request exception."""
        data = super().__init__(request, host, 400, error)

        LOG.error(f'400 ERROR MESSAGE: {error}')
        raise web.HTTPBadRequest(content_type="application/json", body=json.dumps(data).encode('utf-8'))


class BeaconUnauthorised(BeaconError):
    """Raise an HTTP Exception returns with 401 code with a custom error message.

    The method is called if the user is not registered or if the token from the authentication has expired.
    Used in conjuction with Token authentication aiohttp middleware.
    """

    def __init__(self, request, host, error):
        """Return custom unauthorized exception."""
        data = super().__init__(request, host, 401, error)

        LOG.error(f'401 ERROR MESSAGE: {error}')
        raise web.HTTPUnauthorized(content_type="application/json", body=json.dumps(data).encode('utf-8'))


class BeaconForbidden(BeaconError):
    """Raise an HTTP Exception returns with 403 code with the error message.

    `'Resource not granted for authenticated user or resource protected for all users.'`. The method is called if the dataset
    is protected or if the user is authenticated but not granted the resource.
    Used in conjuction with Token authentication aiohttp middleware.
    """

    def __init__(self, request, host, error):
        """Return custom forbidden exception."""
        data = super().__init__(request, host, 403, error)

        LOG.error(f'403 ERROR MESSAGE: {error}')
        raise web.HTTPUnauthorized(content_type="application/json", body=json.dumps(data).encode('utf-8'))

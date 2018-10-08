"""Custom API exception reponses.

API specification requires custom messages upon error.
"""

import json
from aiohttp import web
from .. import __apiVersion__
from ..utils.logging import LOG


class BeaconError(Exception):
    """BeaconError Exception specific class.

    Generates custom exception messages based on request parameters.
    """

    def __init__(self, request, host, error_code, error):
        """Return request data as dictionary."""
        self.data = {'beaconId': '.'.join(reversed(host.split('.'))),
                     "apiVersion": __apiVersion__,
                     'exists': None,
                     'error': {'errorCode': error_code,
                               # 'Bad request, missing mandatory parameter or the value is not valid!'
                               'errorMessage': error},
                     # TO DO see if we still need the default values now that we take them from schema
                     'alleleRequest': {'referenceName': request.get("referenceName"),
                                       'start': request.get("start", 0),
                                       'startMin': request.get("startMin", 0),
                                       'startMax': request.get("startMax", 0),
                                       'end': request.get("end", 0),
                                       'endMin': request.get("endMin", 0),
                                       'endMax': request.get("endMax", 0),
                                       'referenceBases': request.get("referenceBases"),
                                       'assemblyId': request.get("assemblyId", ""),
                                       'datasetIds': request.get("datasetIds", []),
                                       'includeDatasetResponses': request.get("includeDatasetResponses", "NONE"), },
                     'datasetAlleleResponses': []}
        required_alternative = ["alternateBases", "variantType"]
        self.data['alleleRequest'].update({k: request.get(k) for k in required_alternative if k in request})
        return self.data


class BeaconBadRequest(BeaconError):
    """Exception returns with 400 code and a custom error message.

    The method is called if one of the required parameters are missing or invalid.
    Used in conjuction with JSON Schema validator.
    """

    def __init__(self, request, host, error):
        """Return custom bad request exception."""
        data = super().__init__(request, host, 400, error)

        LOG.error(f'400 ERROR MESSAGE: {error}')
        raise web.HTTPBadRequest(content_type="application/json", body=json.dumps(data).encode('utf-8'))


class BeaconUnauthorised(BeaconError):
    """HTTP Exception returns with 401 code with a custom error message.

    The method is called if the user is not registered or if the token from the authentication has expired.
    Used in conjuction with Token authentication aiohttp middleware.
    """

    def __init__(self, request, host, error):
        """Return custom unauthorized exception."""
        data = super().__init__(request, host, 401, error)

        LOG.error(f'401 ERROR MESSAGE: {error}')
        raise web.HTTPUnauthorized(content_type="application/json", body=json.dumps(data).encode('utf-8'))


class BeaconForbidden(BeaconError):
    """HTTP Exception returns with 403 code with the error message.

    `'Resource not granted for authenticated user or resource protected for all users.'`.
    The method is called if the dataset is protected or if the user is authenticated
    but not granted the resource. Used in conjuction with Token authentication aiohttp middleware.
    """

    def __init__(self, request, host, error):
        """Return custom forbidden exception."""
        data = super().__init__(request, host, 403, error)

        LOG.error(f'403 ERROR MESSAGE: {error}')
        raise web.HTTPUnauthorized(content_type="application/json", body=json.dumps(data).encode('utf-8'))


class BeaconServerError(BeaconError):
    """HTTP Exception returns with 500 code with the error message.

    The 500 error is not specified by the Beacon API, thus as simple error would do.
    """

    def __init__(self, error):
        """Return custom forbidden exception."""
        data = {'errorCode': 500,
                'errorMessage': error}

        LOG.error(f'500 ERROR MESSAGE: {error}')
        raise web.HTTPUnauthorized(content_type="application/json", body=json.dumps(data).encode('utf-8'))

"""Custom API exception reponses.

API specification requires custom messages upon error.
"""

import json
from typing import Dict
from aiohttp import web
from .. import __apiVersion__
from ..utils.logging import LOG
from ..conf import CONFIG_INFO


def process_exception_data(request: web.Request,
                           host: str,
                           error_code: int,
                           error: str) -> Dict:
    """Return request data as dictionary.

    Generates custom exception messages based on request parameters.
    """
    data = {'beaconId': '.'.join(reversed(host.split('.'))),
            "apiVersion": __apiVersion__,
            'exists': None,
            'error': {'errorCode': error_code,
                      'errorMessage': error},
            'alleleRequest': {'referenceName': request.get("referenceName", None),
                              'referenceBases': request.get("referenceBases", None),
                              'includeDatasetResponses': request.get("includeDatasetResponses", "NONE"),
                              'assemblyId': request.get("assemblyId", None)},
            # showing empty datasetsAlleRsponse as no datasets found
            # A null/None would represent no data while empty array represents
            # none found or error and corresponds with exists null/None
            'datasetAlleleResponses': []}
    # include datasetIds only if they are specified
    # as per specification if they don't exist all datatsets will be queried
    # Only one of `alternateBases` or `variantType` is required, validated by schema
    oneof_fields = ["alternateBases", "variantType", "start", "end", "startMin", "startMax",
                    "endMin", "endMax", "datasetIds"]
    data['alleleRequest'].update({k: request.get(k) for k in oneof_fields if k in request})

    return data


class BeaconBadRequest(web.HTTPBadRequest):
    """Exception returns with 400 code and a custom error message.

    The method is called if one of the required parameters are missing or invalid.
    Used in conjunction with JSON Schema validator.
    """

    def __init__(self, request: web.Request,
                 host: str, error: str) -> None:
        """Return custom bad request exception."""
        data = process_exception_data(request, host, 400, error)
        super().__init__(text=json.dumps(data), content_type="application/json")
        LOG.error(f'401 ERROR MESSAGE: {error}')


class BeaconUnauthorised(web.HTTPUnauthorized):
    """HTTP Exception returns with 401 code with a custom error message.

    The method is called if the user is not registered or if the token from the authentication has expired.
    Used in conjunction with Token authentication aiohttp middleware.
    """

    def __init__(self, request: web.Request,
                 host: str, error: str, error_message: str) -> None:
        """Return custom unauthorized exception."""
        data = process_exception_data(request, host, 401, error)
        headers_401 = {"WWW-Authenticate": f"Bearer realm=\"{CONFIG_INFO.url}\"\n\
                         error=\"{error}\"\n\
                         error_description=\"{error_message}\""}
        super().__init__(content_type="application/json", text=json.dumps(data),
                         # we use auth scheme Bearer by default
                         headers=headers_401)
        LOG.error(f'401 ERROR MESSAGE: {error}')


class BeaconForbidden(web.HTTPForbidden):
    """HTTP Exception returns with 403 code with the error message.

    `'Resource not granted for authenticated user or resource protected for all users.'`.
    The method is called if the dataset is protected or if the user is authenticated
    but not granted the resource. Used in conjunction with Token authentication aiohttp middleware.
    """

    def __init__(self, request: web.Request,
                 host: str, error: str) -> None:
        """Return custom forbidden exception."""
        data = process_exception_data(request, host, 403, error)
        super().__init__(content_type="application/json", text=json.dumps(data))
        LOG.error(f'403 ERROR MESSAGE: {error}')


class BeaconServerError(web.HTTPInternalServerError):
    """HTTP Exception returns with 500 code with the error message.

    The 500 error is not specified by the Beacon API, thus as simple error would do.
    """

    def __init__(self, error: str) -> None:
        """Return custom forbidden exception."""
        data = {'errorCode': 500,
                'errorMessage': error}
        super().__init__(content_type="application/json", text=json.dumps(data))
        LOG.error(f'500 ERROR MESSAGE: {error}')

"""Query Endpoint.

The query endpoint provides means of retrieving information about specific
reference + alternate bases/variant type combination, as well as matching
start or end position.
"""

from ..utils.logging import LOG
from .. import __apiVersion__
from ..utils.data_query import filter_exists, find_datasets, fetch_datasets_access
from .exceptions import BeaconUnauthorised, BeaconForbidden


def access_resolution(request, token, host, public_data, registered_data, controlled_data):
    """Determine the access level for a user.

    Depends on user bona_fide_status, and by default it should be PUBLIC.
    """
    permissions = []
    # all should have access to PUBLIC datasets
    # unless the request is for specific datasets
    if public_data:
        permissions.append("PUBLIC")
    access = set(public_data)  # empty if no datasets are given

    # for now we are expecting that the permissions are a list of datasets
    if registered_data and token["bona_fide_status"] is True:
        permissions.append("REGISTERED")
        access = access.union(set(registered_data))
    # if user requests public datasets do not throw an error
    # if both registered and controlled datasets are request this will be shown first
    elif registered_data and not public_data:
        if not token["bona_fide_status"]:
            # token is not provided (user not authed)
            raise BeaconUnauthorised(request, host, 'Unauthorized access to dataset(s).')
        # token is present, but is missing perms (user authed but no access)
        raise BeaconForbidden(request, host, 'Access to dataset(s) is forbidden.')
    if controlled_data and 'permissions' in token and token['permissions']:
        # The idea is to return only accessible datasets

        # Default event, when user doesn't specify dataset ids
        # Contains only dataset ids from token that are present at beacon
        controlled_access = set(controlled_data).intersection(set(token['permissions']))
        access = access.union(controlled_access)
        if controlled_access:
            permissions.append("CONTROLLED")
    # if user requests public datasets do not throw an error
    elif controlled_data and not public_data:
        if not token['permissions']:
            # token is not provided (user not authed)
            raise BeaconUnauthorised(request, host, 'Unauthorized access to dataset(s).')
        # token is present, but is missing perms (user authed but no access)
        raise BeaconForbidden(request, host, 'Access to dataset(s) is forbidden.')
    LOG.info(f"Accesible datasets are: {list(access)}.")
    return permissions, list(access)


async def query_request_handler(params):
    """Handle the parameters of the query endpoint in order to find the required datasets.

    params = db_pool, method, request, token, host
    """
    LOG.info(f'{params[1]} request to beacon endpoint "/query"')
    request = params[2]
    # Fills the Beacon variable with the found data.
    position = (request.get("start", 0), request.get("end", 0),
                request.get("startMin", 0), request.get("startMax", 0),
                request.get("endMin", 0), request.get("endMax", 0))
    alleleRequest = {'referenceName': request.get("referenceName"),
                     'start': position[0],
                     'startMin': position[2],
                     'startMax': position[3],
                     'end': position[1],
                     'endMin': position[4],
                     'endMax': position[5],
                     'referenceBases': request.get("referenceBases"),
                     'assemblyId': request.get("assemblyId"),
                     'datasetIds': request.get("datasetIds", []),
                     'includeDatasetResponses': request.get("includeDatasetResponses", "NONE")}
    required_alternative = ["alternateBases", "variantType"]
    alleleRequest.update({k: request.get(k) for k in required_alternative if k in request})
    alternate = alleleRequest.get("variantType"), alleleRequest.get("alternateBases")

    # Get dataset ids that were requested, sort by access level
    # If request is empty (default case) the three dataset variables contain all datasets by access level
    # Datasets are further filtered using permissions from token
    public_datasets, registered_datasets, controlled_datasets = await fetch_datasets_access(params[0], request.get("datasetIds"))
    access_type, accessible_datasets = access_resolution(request, params[3], params[4], public_datasets,
                                                         registered_datasets, controlled_datasets)

    datasets = await find_datasets(params[0], request.get("assemblyId"), position, request.get("referenceName"),
                                   request.get("referenceBases"), alternate,
                                   accessible_datasets, access_type, request.get("includeDatasetResponses", "NONE"))

    beacon_response = {'beaconId': '.'.join(reversed(params[4].split('.'))),
                       'apiVersion': __apiVersion__,
                       'exists': any([x['exists'] for x in datasets]),
                       # Error is not required and should not be shown
                       # If error key is set to null it will still not validate as it has a required key errorCode
                       # otherwise schema validation will fail
                       # "error": None,
                       'alleleRequest': alleleRequest,
                       'datasetAlleleResponses': filter_exists(request.get("includeDatasetResponses", "NONE"), datasets)}

    return beacon_response

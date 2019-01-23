"""Query Endpoint.

The query endpoint provides means of retrieving information about specific
reference + alternate bases/variant type combination, as well as matching
start or end position.
"""

from ..utils.logging import LOG
from .. import __apiVersion__
from ..utils.data_query import filter_exists, find_datasets, fetch_controlled_datasets


def access_resolution(request, token, controlled_data, dataset_ids):
    """Determine the access level for a user.

    Depends on user bona_fide_status, and by default it should be PUBLIC.
    """
    permissions = ["PUBLIC"]
    access = dataset_ids
    # TO DO check if the permissions reflect actual datasets
    # for now we are expecting that eh permissions are a list of datasets
    if token["bona_fide_status"]:
        permissions.append("REGISTERED")
    if 'permissions' in token and token['permissions']:
        # The idea is to return only accessible datasets
        # TO DO test the logic of these set operations
        access = list(set(controlled_data).difference(set(token['permissions'])).union(set(dataset_ids)))
        if access:
            permissions.append("CONTROLLED")
        else:
            pass
            # raise BeaconForbidden(obj, request.host, 'One or more requested datasets are not available for this user.')
    return permissions, access


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

    controlled_datasets = await fetch_controlled_datasets(params[0], request.get("datasetIds"))
    access_type, accessible_datasets = access_resolution(request, params[3], controlled_datasets, request.get("datasetIds"))

    datasets = await find_datasets(params[0], request.get("assemblyId"), position, request.get("referenceName"),
                                   request.get("referenceBases"), alternate,
                                   accessible_datasets, access_type, request.get("includeDatasetResponses", "NONE"))

    beacon_response = {"beaconId": '.'.join(reversed(params[4].split('.'))),
                       "apiVersion": __apiVersion__,
                       "exists": any([x['exists'] for x in datasets]),
                       # Error is not required and should not be shown
                       # If error key is set to null it will still not validate as it has a required key errorCode
                       # otherwise schema validation will fail
                       # "error": None,
                       "alleleRequest": alleleRequest,
                       "datasetAlleleResponses": filter_exists(request.get("includeDatasetResponses", "NONE"), datasets)}

    return beacon_response

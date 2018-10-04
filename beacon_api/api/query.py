from ..utils.logging import LOG
from .. import __apiVersion__
from ..utils.data_query import filter_exists, find_datasets


def query_request_handler(method, request, token, host):
    """
    """
    LOG.info(f'{method} request to beacon endpoint "/query"')

    # Fills the Beacon variable with the found data.
    alleleRequest = {'referenceName': request.get("referenceName"),
                     'start': request.get("start"),
                     'startMin': request.get("startMin", 0),
                     'startMax': request.get("startMax", 0),
                     'end': request.get("end", 0),
                     'endMin': request.get("endMin", 0),
                     'endMax': request.get("endMax", 0),
                     'referenceBases': request.get("referenceBases"),
                     'assemblyId': request.get("assemblyId", 0),
                     'datasetIds': request.get("datasetIds", []),
                     'includeDatasetResponses': request.get("includeDatasetResponses", "NONE")}
    required_alternative = ["alternateBases", "variantType"]
    alleleRequest.update({k: request.get(k) for k in required_alternative if k in request})

    datasets = find_datasets(request, token)

    beacon_response = {"beaconId": '.'.join(reversed(host.split('.'))),
                       "apiVersion": __apiVersion__,
                       # 'exists': checkifdatasetisTrue(datasetAlleleResponses),
                       "exists": None,
                       "error": None,
                       "alleleRequest": alleleRequest,
                       "datasetAlleleResponses": filter_exists(request.get("includeDatasetResponses", "NONE"), datasets)}

    return beacon_response

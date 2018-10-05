from ..utils.logging import LOG
from .. import __apiVersion__
from ..utils.data_query import filter_exists, find_datasets


async def query_request_handler(params):
    """Handle the parameters of the query endpoint in order to find the required datasets.

    params = db_pool, method, request, token, host
    """
    LOG.info(f'{params[1]} request to beacon endpoint "/query"')
    request = params[2]
    # Fills the Beacon variable with the found data.
    position = (request.get("start"), request.get("end", 0),
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
                     'assemblyId': request.get("assemblyId", "GRCh38"),
                     'datasetIds': request.get("datasetIds", []),
                     'includeDatasetResponses': request.get("includeDatasetResponses")}
    required_alternative = ["alternateBases", "variantType"]
    alleleRequest.update({k: request.get(k) for k in required_alternative if k in request})
    alternate = alleleRequest.get("variantType"), alleleRequest.get("alternateBases")

    datasets = await find_datasets(params[0], position, alternate, request.get("datasetIds"), params[3])

    beacon_response = {"beaconId": '.'.join(reversed(params[4].split('.'))),
                       "apiVersion": __apiVersion__,
                       "exists": any(list(map(lambda x: x["exists"], datasets))),
                       "error": None,
                       "alleleRequest": alleleRequest,
                       "datasetAlleleResponses": filter_exists(request.get("includeDatasetResponses", "NONE"), datasets)}

    return beacon_response

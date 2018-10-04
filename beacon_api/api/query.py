from ..utils.logging import LOG
from .. import __apiVersion__, __title__, __version__


def query_request_handler(method, parameters, token, host):
    """
    """
    LOG.info(f'{method} request to beacon endpoint "/query"')
    LOG.debug(parameters)
    emptyDatasetIds = False
    # ----------------------------------------------------------------------------------------------------------------------
    #                                           AUTHENTICATION
    # ----------------------------------------------------------------------------------------------------------------------
    # Variable to declare if the user is authenticated. Changed to true if the token sent in the request is valid.


    if not authenticated:
        # If the user is not authenticated and the user didn't specify the data sets. Then the datasetIds will only
        # contain datasets with PUBLIC as accessType.
        if datasetIds == []:
            # The emptyDatasetIds variable is set to true so that the response will be correct, (datasetIds = []) because the
            # user didn't specify these
            emptyDatasetIds = True
            rows = Beacon_dataset_table.query.all()
            for row in rows:
                if row.accessType == 'PUBLIC':
                    # append if the accessType is PUBLIC
                    datasetIds.append(row.name)
            LOG.debug(' * datasetIds: {}'.format(datasetIds))

        datasetObject = Beacon_dataset_table.query.all()
        for set in datasetObject:
            LOG.debug(' * {}: {}'.format(set.name, set.accessType))
            # If the user wants to access a protected data set and has not been authorized.
            if set.accessType != 'PUBLIC' and set.name in datasetIds:
                LOG.warning(
                    ' * * * 401 ERROR MESSAGE: User not authorized to access data set: {}'.format(set.name))

    LOG.debug(' * The datasetIds list has now the following items : {}'.format(datasetIds))
    # ----------------------------------------------------------------------------------------------------------------------
    #                           PARAMETER CHECKING AND RESPONSE CONSTRUCTION
    # ----------------------------------------------------------------------------------------------------------------------
    datasetAlleleResponses, true_datasetAlleleResponses, false_datasetAlleleResponses, includeDatasetResponses = checkParameters(
        referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType,
        assemblyId, datasetIds, includeDatasetResponses, error_)

    # If the user didn't specify any data sets.
    if emptyDatasetIds:
        datasetIds = []

    # Fills the Beacon variable with the necessary info from the constructor function in beacon_info.
    Beacon = constructor()
    logging.info(' * Received parameters passed the checkParameters() function')
    alleleRequest = {'referenceName': referenceName, 'start': start, 'startMin': startMin, 'startMax': startMax, 'end': end, 'endMin': endMin,
                     'endMax': endMax, 'referenceBases': referenceBases, 'alternateBases': alternateBases, 'variantType': variantType,
                     'assemblyId': assemblyId, 'datasetIds': datasetIds, 'includeDatasetResponses': includeDatasetResponses}

    beacon_response = {'beaconId': '.'.join(reversed(host.split('.'))),
                       "apiVersion": __apiVersion__,
                       'exists': checkifdatasetisTrue(datasetAlleleResponses),
                       'error': None,
                       'alleleRequest': alleleRequest,
                       'datasetAlleleResponses': checkInclude(includeDatasetResponses, datasetAlleleResponses, true_datasetAlleleResponses,
                                                                   false_datasetAlleleResponses)
                            }
    return beacon_response

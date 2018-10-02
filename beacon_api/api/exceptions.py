import json
from aiohttp import web
from .. import __beaconId__, __apiVersion__


class BeaconError(Exception):
    """Initialize the `Beaconerror` object with the parameters that has been received from the users request.

    :type referenceName: String
    :param referenceName: Reference name (chromosome). Accepting values 1-22, X, Y so follows Ensembl chromosome naming convention.
    :type start: Integer
    :param start:
            I. START ONLY:

            - for single positions, e.g. the `start` of a specified sequence alteration where the size is given through the specified `alternateBases`
            - typical use are queries for SNV and small InDels
            - the use of `start` without an `end` parameter requires the use of `referenceBases`
            II. START AND END:

            - special use case for exactly determined structural changes
    :type startMin: Integer
    :param startMin: Minimum start coordinate

            - startMin + startMax + endMin + endMax:
            - for querying imprecise positions (e.g. identifying all structural variants starting anywhere between `startMin` <-> `startMax`, and ending
            anywhere between `endMin` <-> `endMax`
            - single or double sided precise matches can be achieved by setting `startMin` = `startMax` OR `endMin` = `endMax`
    :type startMax: Integer
    :param startMax: Maximum start coordinate. See `startMin`.
    :type end: Integer
    :param end: Precise end coordinate. See `start`.
    :type endMin: Integer
    :param endMin: Minimum end coordinate. See `startMin`.
    :type endMax: Integer
    :param endMax: Maximum end coordinate. See `startMin`.
    :type referenceBases: String
    :param referenceBases: Reference bases for this variant (starting from `start`). Accepted values: [ACGT]* When querying for variants without specific
     base alterations (e.g. imprecise structural variants with separate variantType as well as startMin & endMin ... parameters), the use of a single
      "N" value is required. See the REF field in VCF 4.2 specification.
    :type alternateBases: String
    :param alternateBases: The bases that appear instead of the reference bases. Accepted values: [ACGT]* or N.
            Symbolic ALT alleles (DEL, INS, DUP, INV, CNV, DUP:TANDEM, DEL:ME, INS:ME) will be represented in `variantType`.
            See the ALT field in VCF 4.2 specification
            Either `alternateBases` OR `variantType` is REQUIRED
    :type variantType: String
    :param variantType: The `variantType` is used to denote e.g. structural variants.
            Either `alternateBases´ OR `variantType` is REQUIRED
    :type assemblyId: String
    :param assemblyId: Assembly identifier
    :type datasetIds: String
    :param datasetIds: Identifiers of data sets, as defined in `BeaconDataset`. In case assemblyId doesn't match requested dataset(s) error will be
    raised (400 Bad request). If this field is not specified, all datasets should be queried.
    :type includeDatasetResponses: String
    :param includeDatasetResponses: Indicator of whether responses for individual data sets (`datasetAlleleResponses`) should be included in the
    response (`BeaconAlleleResponse`) to this request or not. If null (not specified), the default value of NONE is assumed.
            Accepted values : ['ALL', 'HIT', 'MISS', 'NONE']
    """

    def __init__(self, request, error_code, error):
        """Return sth."""
        self.data = {'beaconId': __beaconId__,
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
    """
    Stop the actions of the api and returns a 400 error code and a customised error message.

    The method is called if one of the required parameters are missing or invalid.

    :type message: String
    :param message: The error message.
    """

    def __init__(self, request, error):
        """Return sth."""
        data = BeaconError.__init__(self, request, 400, error)

        raise web.HTTPBadRequest(content_type="application/json", body=json.dumps(data).encode('utf-8'))


class BeaconUnauthorised(BeaconError):
    """
    Stop the actions of the api and returns a 401 error code with a custom error message.

    The method is called if the user isn't registered or if the token from the authentication has expired.

    :type message: String
    :param message:
    """

    def __init__(self, request, error):
        """Return sth."""
        data = BeaconError.__init__(self, request, 401, error)

        raise web.HTTPUnauthorized(content_type="application/json", body=json.dumps(data).encode('utf-8'))


class BeaconForbidden(BeaconError):
    """
    Stop the actions of the api and returns a 403 error code with the error message.

    `'Resource not granted for authenticated user or resource protected for all users.'`. The method is called if the dataset
    is protected or if the user is authenticated but not granted the resource.

    :type message: String
    :param message:
    """

    def __init__(self, request, error):
        """Return sth."""
        data = BeaconError.__init__(self, request, 403, error)

        raise web.HTTPUnauthorized(content_type="application/json", body=json.dumps(data).encode('utf-8'))

from flask import request, Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from webargs import fields
from webargs.flaskparser import use_kwargs
import jwt
import logging
# ----------------------------------------------------------------------------------------------------------------------
#                                   APPLICATION SET UPP AND CONFIGURATION
# ----------------------------------------------------------------------------------------------------------------------

# Takes the url and the necessary info for the postgres server from the environmental variables and packs it into one
# variable called DB_URL. The variable is then used to configure the application to connect to that database using
# SQLAlchemy.
URL = os.environ.get('DATABASE_URL').split('/')[2]
POSTGRES = {
    'user': os.environ.get('DATABASE_USER'),
    'password': os.environ.get('DATABASE_PASSWORD'),
    'database': os.environ.get('DATABASE_NAME'),
    'host': URL,
}
DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES['user'], pw=POSTGRES['password'], url=POSTGRES['host'], db=POSTGRES['database'])


application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)
api = Api(application)

# Sets the logging level from environmental variable.
LOGGING_LVL = os.environ.get('LOGGING_LVL')
if LOGGING_LVL == 'DEBUG':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
elif LOGGING_LVL == 'INFO':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
elif LOGGING_LVL == 'WARNING':
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s:%(levelname)s:%(message)s')
elif LOGGING_LVL == 'CRITICAL':
    logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s:%(levelname)s:%(message)s')


from check_functions import *
from error_handelers import BeaconError
import beacon_info
from models import *

# Creates the emptyDatasetIds database tables if they are not all ready created. The application doesen't need pre
# filled tables to
# work , but it does need the tables to exist.
db.create_all()
#
# ----------------------------------------------------------------------------------------------------------------------
#                                         INFO END POINT OPERATIONS
# ----------------------------------------------------------------------------------------------------------------------


class Beacon_get(Resource):
    """
    The Beacon_get class contains the operations for the "/" end point. The "/" end point only serves as an info
    endpoint. It inherits properties from flask_restfuls Resource class.
    """
    def get(self):
        """
        The `get()` method in the `Beacon_get class` uses the HTTP protocol 'GET' to return a Json object of all the
        necessary info on the beacon and the Api. It uses the '/' path and only serves an information giver.

        :type Beacon: Dict
        :return Beacon: The method returns the dict Beacon that was constructed in the constructor() function in beacon_info.py
        """

        logging.info(' * Get request to beacon end poit "/"')
        Beacon = beacon_info.constructor()
        print(type(Beacon))
        return Beacon


api.add_resource(Beacon_get, '/')
# ----------------------------------------------------------------------------------------------------------------------
#                                         QUERY END POINT OPERATIONS
# ----------------------------------------------------------------------------------------------------------------------


class Beacon_query(Resource):
    """
    The `Beacon_query class` contains the operations for the `/query` end point. The `/query` end point handles the
    query's to the database and is the end point from which most of the operations are done. It inherits properties
    from flask_restful's Resource class.
    """
    # args takes in the request variables and sets them to the missing value if they are absent.
    args = {
        'referenceName': fields.Str(
            missing='0'
        ),
        'start': fields.Int(
            missing=0
        ),
        'startMin': fields.Int(
            missing=0
        ),
        'startMax': fields.Int(
            missing=0
        ),
        'end': fields.Int(
            missing=0
        ),
        'endMin': fields.Int(
            missing=0
        ),
        'endMax': fields.Int(
            missing=0
        ),
        'referenceBases': fields.Str(
            missing='0'
        ),
        'alternateBases': fields.Str(
            missing='0'
        ),
        'variantType': fields.Str(
            missing='0'
        ),
        'assemblyId': fields.Str(
            missing='0'
        ),
        'datasetIds': fields.List(fields.Str(), missing=[]),
        'includeDatasetResponses': fields.Str(
            missing='ALL',
        ),
    }

    @use_kwargs(args)
    def get(self, referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId, datasetIds,
            includeDatasetResponses):
        """
        The `get()` method of the `Beacon_query class` gets it's parameters from the `@use_kwargs(args)` decorator and uses the HTTP
        protocol `GET` to return a Json object. The object contains the `alleleRequest` that was submitted, the `datasetAlleleResponse`
        that was received, some general info on the api and the parameter `exists`. The exists parameter is the answer from the
        query that tells the user if the allele was found or not.
        But first the methods creates the BeaconError object `error_` so it can use it's error handlers. Then it checks that the
        submitted parameters are valid and gets the `datasetAlleleResponses` and the `includeDatasetResponses` from the
        `checkParameters()` method.

        :type referenceName: String
        :param referenceName: Reference name (chromosome). Accepting values 1-22, X, Y so follows Ensembl chromosome naming convention.
        :type start: Integer
        :param start:
                `start` only:

                - for single positions, e.g. the `start` of a specified sequence alteration where the size is given through the specified `alternateBases`
                - typical use are queries for SNV and small InDels
                - the use of `start` without an `end` parameter requires the use of `referenceBases`
                `start` and `end`:

                - special use case for exactly determined structural changes
        :type startMin: Integer
        :param startMin: Minimum start coordinate

                `startMin` + `startMax` + `endMin` + `endMax`:

                - for querying imprecise positions (e.g. identifying all structural variants starting anywhere between `startMin` <-> `startMax`,
                 and ending anywhere between `endMin` <-> `endMax`
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
        :param referenceBases: Reference bases for this variant (starting from `start`). Accepted values: [ACGT]* When querying for variants without
         specific base alterations (e.g. imprecise structural variants with separate variantType as well as startMin & endMin ... parameters), the use
         of a single "N" value is required. See the REF field in VCF 4.2 specification.
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
        :type beaconAlleleResponse: Dict
        :return beaconAlleleResponse: The response that the user receives from the `Beacon`.
        """
        logging.info(' * GET request to beacon endpoit "/query"')
        logging.debug(' * Parameters recived:\nreferenceName: {}\nstart: {}\nstartMin: {}\nstartMax: {}\nend: {}\nendMin: {}\nendMax: {}\nreferenceBases: \
        {}\nsalternateBasestart: {}\nvariantType: {}\nassemblyId: {}\ndatasetIds: {}\nincludeDatasetResponses: {}\n'
                      .format(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId,
                              datasetIds, includeDatasetResponses))
        error_ = BeaconError(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId,
                             datasetIds, includeDatasetResponses)
        emptyDatasetIds = False
# ----------------------------------------------------------------------------------------------------------------------
#                                           AUTHENTICATION
# ----------------------------------------------------------------------------------------------------------------------
        # Variable to declare if the user is authenticated. Changed to true if the token sent in the request is valid.
        authenticated = False
        # gets the token from the request header.
        authHeader = request.headers.get('Authorization')
        if authHeader:
            try:
                # The second item is the token.
                token = authHeader.split(' ')[1]
                key = os.environ.get('PUBLIC_KEY').replace(r'\n', '\n')
                logging.debug(' * TOKEN: {}'.format(token))
                logging.debug(' * KEY: {}'.format(key))
                decodeData = jwt.decode(token, key, algorithms=['RS256'])
                authenticated = True
                logging.debug(' * Token payload: {}'.format(decodeData))
            except Exception as error:
                # If an exception accures when decoding the token --> the token is invalid or expired, then the error
                # message will be sent in the response.
                logging.warning(' * * * 401 ERROR MESSAGE: Authorization failed, token invalid.')
                error_.unauthorised('Authorization failed, token invalid.')

        logging.debug(' * Authenticated: {}'.format(authenticated))

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
                logging.debug(' * datasetIds: {}'.format(datasetIds))

            datasetObject = Beacon_dataset_table.query.all()
            for set in datasetObject:
                logging.debug(' * {}: {}'.format(set.name, set.accessType))
                # If the user wants to access a protected data set and has not been authorized.
                if set.accessType != 'PUBLIC' and set.name in datasetIds:
                    logging.warning(' * * * 401 ERROR MESSAGE: User not authorized to access data set: {}'.format(set.name))
                    error_.unauthorised('User not authorized to access data set: {}'.format(set.name))

        logging.debug(' * The datasetIds list has now the following items : {}'.format(datasetIds))
# ----------------------------------------------------------------------------------------------------------------------
#                            PARAMETER CHECKING AND RESPONSE CONSTRUCTION
# ----------------------------------------------------------------------------------------------------------------------
        datasetAlleleResponses, true_datasetAlleleResponses, false_datasetAlleleResponses, includeDatasetResponses = checkParameters(
            referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId, datasetIds,
            includeDatasetResponses, error_)

        # If the user didn't specify any data sets.
        if emptyDatasetIds:
            datasetIds = []

        # Fills the Beacon variable with the necessary info from the constructor function in beacon_info.
        Beacon = beacon_info.constructor()
        logging.info(' * Received parameters passed the checkParameters() function')
        alleleRequest = {'referenceName': referenceName, 'start': start, 'startMin': startMin, 'startMax': startMax, 'end': end, 'endMin': endMin,
                         'endMax': endMax, 'referenceBases': referenceBases, 'alternateBases': alternateBases, 'variantType': variantType,
                         'assemblyId': assemblyId, 'datasetIds': datasetIds, 'includeDatasetResponses': includeDatasetResponses}

        beaconAlleleResponse = {'beaconId': Beacon['id'],
                                "apiVersion": Beacon['apiVersion'],
                                'exists': checkifdatasetisTrue(datasetAlleleResponses),
                                'error': None,
                                'alleleRequest': alleleRequest,
                                'datasetAlleleResponses': checkInclude(includeDatasetResponses, datasetAlleleResponses, true_datasetAlleleResponses,
                                                                       false_datasetAlleleResponses)
                                }
        return beaconAlleleResponse

    @use_kwargs(args)
    def post(self, referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId, datasetIds,
             includeDatasetResponses):
        """
        The `post()` method runs the same code as the `get()´ method but uses the HTTP protocol `POST` instead. The main difference
        between the methods is that the parameters are not sent in the URL. This is more secure because the `GET` requests URLs get
        logged and if you use the `POST´ instead, you don't reveal the parameters that you query with.

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
                - for querying imprecise positions (e.g. identifying all structural variants starting anywhere between `startMin` <-> `startMax`, and
                 ending anywhere between `endMin` <-> `endMax`
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
        :param referenceBases: Reference bases for this variant (starting from `start`). Accepted values: [ACGT]* When querying for variants without
         specific base alterations (e.g. imprecise structural variants with separate variantType as well as startMin & endMin ... parameters), the use
          of a single "N" value is required. See the REF field in VCF 4.2 specification.
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
        :param datasetIds: Identifiers of data sets, as defined in `BeaconDataset`. In case assemblyId doesn't match requested dataset(s) error will
         be raised (400 Bad request). If this field is not specified, all datasets should be queried.
        :type includeDatasetResponses: String
        :param includeDatasetResponses: Indicator of whether responses for individual data sets (`datasetAlleleResponses`) should be included in the
         response (`BeaconAlleleResponse`) to this request or not. If null (not specified), the default value of NONE is assumed.
                Accepted values : ['ALL', 'HIT', 'MISS', 'NONE']
        :type beaconAlleleResponse: Dict
        :return beaconAlleleResponse: The response that the user receives from the `Beacon`.
        """
        logging.info(' * POST request to beacon endpoit "/query"')
        logging.debug(
            ' * Parameters recived:\nreferenceName: {}\nstart: {}\nstartMin: {}\nstartMax: {}\nend: {}\nendMin: {}\nendMax: {}\nreferenceBases: \
            {}\nsalternateBasestart: {}\nvariantType: {}\nassemblyId: {}\ndatasetIds: {}\nincludeDatasetResponses: {}\n'.format(
                referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases,
                variantType, assemblyId, datasetIds, includeDatasetResponses))
        error_ = BeaconError(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases,
                             alternateBases, variantType, assemblyId, datasetIds, includeDatasetResponses)
        emptyDatasetIds = False
# ----------------------------------------------------------------------------------------------------------------------
#                                           AUTHENTICATION
# ----------------------------------------------------------------------------------------------------------------------
        # Variable to declare if the user is authenticated. Changed to true if the token sent in the request is valid.
        authenticated = False
        # gets the token from the request header.
        authHeader = request.headers.get('Authorization')
        if authHeader:
            try:
                # The second item is the token.
                token = authHeader.split(' ')[1]
                key = os.environ.get('PUBLIC_KEY').replace(r'\n', '\n')
                logging.debug(' * TOKEN: {}'.format(token))
                logging.debug(' * KEY: {}'.format(key))
                decodeData = jwt.decode(token, key, algorithms=['RS256'])
                authenticated = True
                logging.debug(' * Token payload: {}'.format(decodeData))
            except Exception as error:
                # If an exception accures when decoding the token --> the token is invalid or expired, then the error
                # message will be sent in the response.
                logging.warning(' * * * 401 ERROR MESSAGE: Authorization failed, token invalid.')
                error_.unauthorised('Authorization failed, token invalid.')

        logging.debug(' * Authenticated: {}'.format(authenticated))

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
                logging.debug(' * datasetIds: {}'.format(datasetIds))

            datasetObject = Beacon_dataset_table.query.all()
            for set in datasetObject:
                logging.debug(' * {}: {}'.format(set.name, set.accessType))
                # If the user wants to access a protected data set and has not been authorized.
                if set.accessType != 'PUBLIC' and set.name in datasetIds:
                    logging.warning(
                        ' * * * 401 ERROR MESSAGE: User not authorized to access data set: {}'.format(set.name))
                    error_.unauthorised('User not authorized to access data set: {}'.format(set.name))

        logging.debug(' * The datasetIds list has now the following items : {}'.format(datasetIds))
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
        Beacon = beacon_info.constructor()
        logging.info(' * Received parameters passed the checkParameters() function')
        alleleRequest = {'referenceName': referenceName, 'start': start, 'startMin': startMin, 'startMax': startMax, 'end': end, 'endMin': endMin,
                         'endMax': endMax, 'referenceBases': referenceBases, 'alternateBases': alternateBases, 'variantType': variantType,
                         'assemblyId': assemblyId, 'datasetIds': datasetIds, 'includeDatasetResponses': includeDatasetResponses}

        beaconAlleleResponse = {'beaconId': Beacon['id'],
                                "apiVersion": Beacon['apiVersion'],
                                'exists': checkifdatasetisTrue(datasetAlleleResponses),
                                'error': None,
                                'alleleRequest': alleleRequest,
                                'datasetAlleleResponses': checkInclude(includeDatasetResponses, datasetAlleleResponses, true_datasetAlleleResponses,
                                                                       false_datasetAlleleResponses)
                                }
        return beaconAlleleResponse


api.add_resource(Beacon_query, '/query')

if __name__ == '__main__':
    application.run(host=os.environ.get('HOST'), port=os.environ.get('PORT'), debug=os.environ.get('DEBUG'))

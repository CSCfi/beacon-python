from flask import request, Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from webargs import fields
from webargs.flaskparser import use_kwargs
import jwt
import logging

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
DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES['user'],pw=POSTGRES['password'],url=POSTGRES['host'],db=POSTGRES['database'])


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

# Creates the empty database tables if they are not all ready created. The application doesen't need pre filled tables to
# work , but it does need the tables to exist.
db.create_all()

class Beacon_get(Resource):
    #The `get()` method in the Beacon_get class uses the HTTP protocol 'GET' to returns a Json object of all the nessesary info on the beacon and the Api. It
    #uses the '/' path and only serves an information giver. The parameters that the method returns and their descriptions
    #can be found under the title: Beacon
    logging.info(' * Get request to beacon end poit "/"')
    def get(self):
        # Fills the Beacon variable with the necessary info from the constructor function in beacon_info.
        Beacon = beacon_info.constructor()
        return Beacon

api.add_resource(Beacon_get,'/')


class Beacon_query(Resource):
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
        'datasetIds': fields.List(fields.Str(),
            missing=[]),
        'includeDatasetResponses': fields.Str(
            missing='ALL',
        ),
    }

    # The `get()` method of the Beacon_query class gets it's parameters from the `@use_kwargs(args)` decorator and uses the HTTP
    # protocol 'GET' to return a Json object. The object contains the `alleleRequest` that was submitted, the `datasetAlleleResponse`
    # that was received, some general info on the api and the parameter `exists`. The `exists` parameter is the answer from the
    # query that tells the user if the allele was found or not.
    # But first the methods creates the BeaconError object `error_` so it can use it's error handlers. Then it checks that the
    # submitted parameters are valid and gets the `datasetAllelResponses` and the `includeDatasetResponses` from the
    # `checkParameters()` method.
    @use_kwargs(args)
    def get(self, referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId, datasetIds, includeDatasetResponses):
        logging.info(' * GET request to beacon endpoit "/query"')
        logging.debug(' * Parameters recived:\nreferenceName: {}\nstart: {}\nstartMin: {}\nstartMax: {}\nend: {}\nendMin: {}\nendMax: {}\nreferenceBases: {}\nsalternateBasestart: {}\nvariantType: {}\nassemblyId: {}\ndatasetIds: {}\nincludeDatasetResponses: {}\n'.format(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId, datasetIds, includeDatasetResponses))
        error_ = BeaconError(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType,assemblyId, datasetIds, includeDatasetResponses)
        # Variable to show if the datasetIds is emty. Changed if dataset = [] and checked before printing the response so
        # that the response is empty.
        empty = False
        # Variable to declare if the user is authenticated. Changed to true if the token sent in the request is valid.
        authenticated = False
        # gets the token from the request header.
        auth_header = request.headers.get('Authorization')
        # If the user has tried to authenticate. if no 'Authorization' in the header, this section is skipped.
        if auth_header:
            try:
                # The second item is the token.
                token = auth_header.split(' ')[1]
                key = os.environ.get('PUBLIC_KEY').replace(r'\n', '\n')
                logging.debug(' * TOKEN: {}'.format(token))
                logging.debug(' * KEY: {}'.format(key))
                decode_data = jwt.decode(token, key, algorithms=['RS256'])
                #if expired(testing)
                #decode_data = jwt.decode(split[1], application.config.get('PUBLIC_KEY'), algorithms=['RS256'], options={'verify_exp': False})
                authenticated = True
                logging.debug(' * token payload: {}'.format(decode_data))
            except Exception as error:
                # If an exception accures when decoding the token --> the token is invalid or expired, then the error
                # message will be sent in the response.
                logging.warning(' * * * 401 ERROR MESSAGE: Authorization failed, token invalid.')
                error_.unauthorised('Authorization failed, token invalid.')

        logging.debug(' * authenticated: {}'.format(authenticated))

        # If the user is not authenticated.
        if authenticated == False:
            # If the user is not authenticated and the user didn't specify the data sets. Then the datasetIds will only
            # contain datasets with PUBLIC as accessType.
            if datasetIds == []:
                # The empty variable is set to true so that the response will be correct, (datasetIds = []) because the
                # user didn't specify these
                empty = True
                rows = Beacon_dataset_table.query.all()
                for row in rows:
                    if row.accessType == 'PUBLIC':
                        # append if the accessType is PUBLIC
                        datasetIds.append(row.name)
                logging.debug(' * datasetIds: {}'.format(datasetIds))

            dataset_obj = Beacon_dataset_table.query.all()
            for set in dataset_obj:
                logging.debug(' * {}: {}'.format(set.name, set.accessType))
                # If the user wants to access a protected data set and has not been authorized.
                if set.accessType != 'PUBLIC' and set.name in datasetIds:
                    logging.warning(' * * * 401 ERROR MESSAGE: User not authorized to access data set: {}'.format(set.name))
                    error_.unauthorised('User not authorized to access data set: {}'.format(set.name))

        logging.debug(' * The datasetIds list has now the following items : {}'.format(datasetIds))


        datasetAllelResponses, true_datasetAllelResponses, false_datasetAllelResponses, includeDatasetResponses = checkParameters(
            referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId, datasetIds, includeDatasetResponses, error_)

        # If the user didn't specify any data sets.
        if empty:
            datasetIds = []

        # Fills the Beacon variable with the necessary info from the constructor function in beacon_info.
        Beacon = beacon_info.constructor()

        logging.info(' * Received parameters passed the checkParameters() function')
        allelRequest = {'referenceName': referenceName,
                        'start': start,
                        'startMin': startMin,
                        'startMax': startMax,
                        'end': end,
                        'endMin': endMin,
                        'endMax': endMax,
                        'referenceBases': referenceBases,
                        'alternateBases': alternateBases,
                        'variantType': variantType,
                        'assemblyId': assemblyId,
                        'datasetIds': datasetIds,
                        'includeDatasetResponses': includeDatasetResponses,
                        }
        return {'beaconId': Beacon['id'],
                "apiVersion": Beacon['apiVersion'],
                'exists': checkifdatasetisTrue(datasetAllelResponses),
                'error': None,
                'allelRequest': allelRequest,
                'datasetAllelResponses': checkInclude(includeDatasetResponses, datasetAllelResponses, true_datasetAllelResponses, false_datasetAllelResponses)
                }

    #The `post()` method runs the same code as the `get()` method but uses the HTTP protocol `POST` instead. The main difference
    #between the methods is that the parameters are not sent in the URL. This is more secure because the `GET` requests URLs get
    #logged and then if you use the `POST` instead, you dont reveal the parameters that you query with.

    @use_kwargs(args)
    def post(self, referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType,assemblyId, datasetIds , includeDatasetResponses):
        logging.info(' * POST request to beacon endpoit "/query"')
        logging.debug(' * Parameters recived:\nreferenceName: {}\nstart: {}\nstartMin: {}\nstartMax: {}\nend: {}\nendMin: {}\nendMax: {}\nreferenceBases: {}\nsalternateBasestart: {}\nvariantType: {}\nassemblyId: {}\ndatasetIds: {}\nincludeDatasetResponses: {}\n'.format(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId, datasetIds, includeDatasetResponses))
        error_ = BeaconError(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType,assemblyId, datasetIds, includeDatasetResponses)
        # Variable to show if the datasetIds is emty. Changed if dataset = [] and checked before printing the response so
        # that the response is empty.
        empty = False
        # Variable to declare if the user is authenticated. Changed to true if the token sent in the request is valid.
        authenticated = False
        # gets the token from the request header.
        auth_header = request.headers.get('Authorization')
        # If the user has tried to authenticate. if no 'Authorization' in the header, this section is skipped.
        if auth_header:
            try:
                # The second item is the token.
                token = auth_header.split(' ')[1]
                key = os.environ.get('PUBLIC_KEY').replace(r'\n', '\n')
                logging.debug(' * TOKEN: {}'.format(token))
                logging.debug(' * KEY: {}'.format(key))
                decode_data = jwt.decode(token, key, algorithms=['RS256'])
                #if expired(testing)
                #decode_data = jwt.decode(split[1], application.config.get('PUBLIC_KEY'), algorithms=['RS256'], options={'verify_exp': False})
                authenticated = True
                logging.debug(' * token payload: {}'.format(decode_data))
            except Exception as error:
                # If an exception accures when decoding the token --> the token is invalid or expired, then the error
                # message will be sent in the response.
                logging.warning(' * * * 401 ERROR MESSAGE: Authorization failed, token invalid.')
                error_.unauthorised('Authorization failed, token invalid.')

        logging.debug(' * authenticated: {}'.format(authenticated))

        # If the user is not authenticated.
        if authenticated == False:
            # If the user is not authenticated and the user didn't specify the data sets. Then the datasetIds will only
            # contain datasets with PUBLIC as accessType.
            if datasetIds == []:
                # The empty variable is set to true so that the response will be correct, (datasetIds = []) because the
                # user didn't specify these
                empty = True
                rows = Beacon_dataset_table.query.all()
                for row in rows:
                    if row.accessType == 'PUBLIC':
                        # append if the accessType is PUBLIC
                        datasetIds.append(row.name)
                logging.debug(' * datasetIds: {}'.format(datasetIds))

            dataset_obj = Beacon_dataset_table.query.all()
            for set in dataset_obj:
                logging.debug(' * {}: {}'.format(set.name, set.accessType))
                # If the user wants to access a protected data set and has not been authorized.
                if set.accessType != 'PUBLIC' and set.name in datasetIds:
                    logging.warning(' * * * 401 ERROR MESSAGE: User not authorized to access data set: {}'.format(set.name))
                    error_.unauthorised('User not authorized to access data set: {}'.format(set.name))

        logging.debug(' * The datasetIds list has now the following items : {}'.format(datasetIds))


        datasetAllelResponses, true_datasetAllelResponses, false_datasetAllelResponses, includeDatasetResponses = checkParameters(
            referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId, datasetIds, includeDatasetResponses, error_)

        # If the user didn't specify any data sets.
        if empty:
            datasetIds = []

        # Fills the Beacon variable with the necessary info from the constructor function in beacon_info.
        Beacon = beacon_info.constructor()

        logging.info(' * Received parameters passed the checkParameters() function')
        allelRequest = {'referenceName': referenceName,
                        'start': start,
                        'startMin': startMin,
                        'startMax': startMax,
                        'end': end,
                        'endMin': endMin,
                        'endMax': endMax,
                        'referenceBases': referenceBases,
                        'alternateBases': alternateBases,
                        'variantType': variantType,
                        'assemblyId': assemblyId,
                        'datasetIds': datasetIds,
                        'includeDatasetResponses': includeDatasetResponses,
                        }
        return {'beaconId': Beacon['id'],
                "apiVersion": Beacon['apiVersion'],
                'exists': checkifdatasetisTrue(datasetAllelResponses),
                'error': None,
                'allelRequest': allelRequest,
                'datasetAllelResponses': checkInclude(includeDatasetResponses, datasetAllelResponses, true_datasetAllelResponses, false_datasetAllelResponses)
                }

api.add_resource(Beacon_query,'/query')

if __name__ == '__main__':
    application.run(host=os.environ.get('HOST'), port=os.environ.get('PORT'), debug=os.environ.get('DEBUG'))
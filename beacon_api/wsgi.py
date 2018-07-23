from flask import request, Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from webargs import fields
from webargs.flaskparser import use_kwargs
import jwt
import logging

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

from beacon_api.check_functions import *
from beacon_api.error_handelers import BeaconError
import beacon_api.beacon_info
import beacon_api.models


class Beacon_get(Resource):
    '''The `get()` method in the Beacon_get class uses the HTTP protocol 'GET' to returns a Json object of all the nessesary info on the beacon and the Api. It
    uses the '/' path and only serves an information giver. The parameters that the method returns and their descriptions
    can be found under the title: Beacon'''''

    logging.info(' * Get request to beacon end poit "/"')
    def get(self):
        Beacon = beacon_api.beacon_info.constructor()
        return Beacon

api.add_resource(Beacon_get,'/')


class Beacon_query(Resource):
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

    '''The `get()` method of the Beacon_query class gets it's parameters from the `@use_kwargs(args)` decorator and uses the HTTP
    protocol 'GET' to return a Json object. The object contains the `alleleRequest` that was submitted, the `datasetAlleleResponse`
    that was received, some general info on the api and the parameter `exists`. The `exists` parameter is the answer from the
    query that tells the user if the allele was found or not.
    ###
    But first the methods creates the BeaconError object `error_` so it can use it's error handlers. Then it checks that the
    submitted parameters are valid and gets the `datasetAllelResponses` and the `includeDatasetResponses` from the 
    `checkParameters()` method.'''

    @use_kwargs(args)
    def get(self, referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId, datasetIds, includeDatasetResponses):
        logging.info(' * GET request to beacon endpoit "/query"')
        logging.debug(' * Parameters recived:\nreferenceName: {}\nstart: {}\nstartMin: {}\nstartMax: {}\nend: {}\nendMin: {}\nendMax: {}\nreferenceBases: {}\nsalternateBasestart: {}\nvariantType: {}\nassemblyId: {}\ndatasetIds: {}\nincludeDatasetResponses: {}\n'.format(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType, assemblyId, datasetIds, includeDatasetResponses))
        error_ = BeaconError(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType,assemblyId, datasetIds, includeDatasetResponses)
        empty = False   # Variable to show if the datasetIds is emty. Changed if dataset = [] and checked befor printing the response so that the response is emty.
        autenticated = False    # Variable to declare if the user is authenticated. Changed to true if the token sent in the request is valid.

        auth_header = request.headers.get('Authorization')  # gets the token from the request header
        if auth_header:     # If the user has tried to authenticate. if no 'Authorization' in the header, this section is skipped
            try:
                split = auth_header.split(' ')  # The second item is the token
                #decode_data = jwt.decode(split[1], app.config.get('PUBLIC_KEY'), algorithms=['RS256'])
                #if expired(testing)
                decode_data = jwt.decode(split[1], app.config.get('PUBLIC_KEY'), algorithms=['RS256'], options={'verify_exp': False})
                autenticated = True
                logging.debug(' * {}'.format(decode_data))
            except Exception as error:
                error_.unauthorised('Authorization failed, token invalid.')

        logging.debug(' * {}'.format(autenticated))
        if autenticated == False:
        #if the user is not authenticatde.
            if datasetIds == []:
            # if the user is not authenticatde and the user didnt specify the datasets. Then the datasetIds will contain datasets with PUBLIC access.
                empty = True    # The emty varable is set to true so that the response will be correct, (datasetIds = []) beacuse the user didnt spesify these
                rows = beacon_api.models.Beacon_dataset_table.query.all()
                for row in rows:
                    if row.accessType == 'PUBLIC':
                        datasetIds.append(row.name)     # append if the accessType is PUBLIC
                logging.debug(' * {}'.format(datasetIds))

            dataset_obj = beacon_api.models.Beacon_dataset_table.query.all()
            for set in dataset_obj:
                logging.debug(' * {}: {}'.format(set.name, set.accessType))
                if set.accessType != 'PUBLIC' and set.name in datasetIds:   # if the user whants to access a protected dataset and has not been authorized.
                    error_.unauthorised('User not authorized to access dataset: {}'.format(set.name))

        logging.debug(' * The datasetIds list has now the following items : {}'.format(datasetIds))


        datasetAllelResponses, true_datasetAllelResponses, false_datasetAllelResponses, includeDatasetResponses = checkParameters(
            referenceName, start, startMin, startMax, end,
            endMin, endMax, referenceBases, alternateBases, variantType,
            assemblyId, datasetIds,
            includeDatasetResponses, error_)

        if empty:      # If the user didnt specify any datasets.
            datasetIds = []

        Beacon = beacon_api.beacon_info.constructor()

        logging.info(' * Recived parameters passed the checkParameters() function')
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

    '''The `post()` method runs the same code as the `get()` method but uses the HTTP protocol `POST` instead. The main difference
    between the methods is that the parameters are not sent in the URL. This is more secure because the `GET` requests URLs get
    logged and then if you use the `POST` instead, you dont reveal the parameters that you query with.'''

    @use_kwargs(args)
    def post(self, referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases, variantType,assemblyId, datasetIds , includeDatasetResponses):
        logging.info(' * POST request to beacon endpoit "/query"')
        logging.debug(
            ' * Parameters recived:\nreferenceName: {}\nstart: {}\nstartMin: {}\nstartMax: {}\nend: {}\nendMin: {}\nendMax: {}\nreferenceBases: {}\nsalternateBasestart: {}\nvariantType: {}\nassemblyId: {}\ndatasetIds: {}\nincludeDatasetResponses: {}\n'.format(
                referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases, alternateBases,
                variantType, assemblyId, datasetIds, includeDatasetResponses))
        error_ = BeaconError(referenceName, start, startMin, startMax, end, endMin, endMax, referenceBases,
                             alternateBases, variantType, assemblyId, datasetIds, includeDatasetResponses)
        empty = False  # Variable to show if the datasetIds is emty. Changed if dataset = [] and checked befor printing the response so that the response is emty.
        autenticated = False  # Variable to declare if the user is authenticated. Changed to true if the token sent in the request is valid.

        auth_header = request.headers.get('Authorization')  # gets the token from the request header
        if auth_header:  # If the user has tried to authenticate. if no 'Authorization' in the header, this section is skipped
            try:
                split = auth_header.split(' ')  # The second item is the token
                # decode_data = jwt.decode(split[1], app.config.get('PUBLIC_KEY'), algorithms=['RS256'])
                # if expired(testing)
                decode_data = jwt.decode(split[1], app.config.get('PUBLIC_KEY'), algorithms=['RS256'],
                                         options={'verify_exp': False})
                autenticated = True
                logging.debug(' * {}'.format(decode_data))
            except Exception as error:
                error_.unauthorised('Authorization failed, token invalid.')

        logging.debug(' * {}'.format(autenticated))
        if autenticated == False:
            # if the user is not authenticatde.
            if datasetIds == []:
                # if the user is not authenticatde and the user didnt specify the datasets. Then the datasetIds will contain datasets with PUBLIC access.
                empty = True  # The emty varable is set to true so that the response will be correct, (datasetIds = []) beacuse the user didnt spesify these
                rows = beacon_api.models.Beacon_dataset_table.query.all()
                for row in rows:
                    if row.accessType == 'PUBLIC':
                        datasetIds.append(row.name)  # append if the accessType is PUBLIC
                logging.debug(' * {}'.format(datasetIds))

            dataset_obj = beacon_api.models.Beacon_dataset_table.query.all()
            for set in dataset_obj:
                logging.debug(' * {}: {}'.format(set.name, set.accessType))
                if set.accessType != 'PUBLIC' and set.name in datasetIds:  # if the user whants to access a protected dataset and has not been authorized.
                    error_.unauthorised('User not authorized to access dataset: {}'.format(set.name))
        logging.debug(' * The datasetIds list has now the following items : {}'.format(datasetIds))

        datasetAllelResponses, true_datasetAllelResponses, false_datasetAllelResponses, includeDatasetResponses = checkParameters(
            referenceName, start, startMin, startMax, end,
            endMin, endMax, referenceBases, alternateBases, variantType,
            assemblyId, datasetIds,
            includeDatasetResponses, error_)

        if empty:  # If the user didnt specify any datasets.
            datasetIds = []

        Beacon = beacon_api.beacon_info.constructor()

        logging.info(' * Recived parameters passed the checkParameters() function')
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
                'datasetAllelResponses': checkInclude(includeDatasetResponses, datasetAllelResponses,
                                                      true_datasetAllelResponses, false_datasetAllelResponses)
                }

api.add_resource(Beacon_query,'/query')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
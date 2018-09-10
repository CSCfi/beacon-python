from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api


# ----------------------------------------------------------------------------------------------------------------------
#                                   APPLICATION SET UPP AND CONFIGURATION
# ----------------------------------------------------------------------------------------------------------------------

# Takes the url and the necessary info for the postgres server from the environmental variables and packs it into one
# variable called DB_URL. The variable is then used to configure the application to connect to that database using
# SQLAlchemy.
URL = os.environ.get('DATABASE_URL', 'postgresql://localhost:5432').split('/')[2]
POSTGRES = {
    'user': os.environ.get('DATABASE_USER', ''),
    'password': os.environ.get('DATABASE_PASSWORD', ''),
    'database': os.environ.get('DATABASE_NAME', 'beacondb'),
    'host': URL,
}
DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES['user'], pw=POSTGRES['password'], url=POSTGRES['host'], db=POSTGRES['database'])


application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)
api = Api(application)

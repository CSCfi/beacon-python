"""DB Configuration.

Specify the url and the necessary info for the PostgreSQL server from the environmental variables and packs it into one
variable called DB_URL. The variable is then used to configure the application to connect to that database using asyncpg.
At this point we also initialize a conection pool that the API is going to use throughout its endpoints.
"""

import os

from configparser import ConfigParser
from collections import namedtuple

import asyncpg


def parse_configuration_file(path):
    """Parses configuration file."""
    config = ConfigParser()
    config.read(path)
    config_vars = {
        'title': config.get('beacon_general_info', 'title'),
        'version': config.get('beacon_general_info', 'version'),
        'author': config.get('beacon_general_info', 'author'),
        'license': config.get('beacon_general_info', 'license'),
        'copyright': config.get('beacon_general_info', 'copyright'),
        'apiVersion': config.get('beacon_api_info', 'apiVersion'),
        'beaconId': config.get('beacon_api_info', 'beaconId'),
        'description': config.get('beacon_api_info', 'description'),
        'url': config.get('beacon_api_info', 'url'),
        'alturl': config.get('beacon_api_info', 'alturl'),
        'createtime': config.get('beacon_api_info', 'createtime'),
        'org_id': config.get('organisation_info', 'org_id'),
        'org_name': config.get('organisation_info', 'org_name'),
        'org_description': config.get('organisation_info', 'org_description'),
        'org_address': config.get('organisation_info', 'org_address'),
        'org_welcomeUrl': config.get('organisation_info', 'org_welcomeUrl'),
        'org_contactUrl': config.get('organisation_info', 'org_contactUrl'),
        'org_logoUrl': config.get('organisation_info', 'org_logoUrl'),
        'org_info': config.get('organisation_info', 'org_info'),
    }
    return namedtuple("Config", config_vars.keys())(*config_vars.values())


URL = os.environ.get('DATABASE_URL', 'postgresql://localhost:5432').split('/')[2]
POSTGRES = {
    'user': os.environ.get('DATABASE_USER', 'beacon'),
    'password': os.environ.get('DATABASE_PASSWORD', 'beacon'),
    'database': os.environ.get('DATABASE_NAME', 'beacondb'),
    'host': URL,
}

DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES['user'],
                                                      pw=POSTGRES['password'],
                                                      url=POSTGRES['host'],
                                                      db=POSTGRES['database'])


async def init_db_pool():
    """Create a connection pool.

    As we will have frequent requests to the database it is recommended to create a connection pool.
    """
    return await asyncpg.create_pool(dsn=DB_URL)

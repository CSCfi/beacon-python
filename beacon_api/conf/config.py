import os
import asyncpg

# ----------------------------------------------------------------------------------------------------------------------
#                                   APPLICATION SET UPP AND CONFIGURATION
# ----------------------------------------------------------------------------------------------------------------------

# Takes the url and the necessary info for the postgres server from the environmental variables and packs it into one
# variable called DB_URL. The variable is then used to configure the application to connect to that database using
# SQLAlchemy.
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

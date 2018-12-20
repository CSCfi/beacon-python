"""DB Configuration.

Specify the URL and the necessary info for the PostgreSQL server from the environmental variables and pack it into one
variable called DB_URL. The variable is then used to configure the application to connect to that database using asyncpg.
At this point we also initialize a connection pool that the API is going to use on all its endpoints.
"""

import os
import asyncpg

DB_SCHEMA = os.environ.get('DATABASE_SCHEMA', '')
DB_SCHEMA += '.' if DB_SCHEMA else ''

async def init_db_pool():
    """Create a connection pool.

    As we will have frequent requests to the database it is recommended to create a connection pool.
    """
    return await asyncpg.create_pool(host=os.environ.get('DATABASE_URL', 'localhost'),
                                     port=os.environ.get('DATABASE_PORT', '5432'),
                                     user=os.environ.get('DATABASE_USER', 'beacon'),
                                     password=os.environ.get('DATABASE_PASSWORD', 'beacon'),
                                     database=os.environ.get('DATABASE_NAME', 'beacondb'),
                                     # initializing with 0 connections allows the web server to
                                     # start and also continue to live
                                     min_size=0,
                                     # for now limiting the number of connections in the pool
                                     max_size=20,
                                     max_queries=50000,
                                     timeout=120,
                                     command_timeout=180,
                                     max_cached_statement_lifetime=0,
                                     max_inactive_connection_lifetime=180)

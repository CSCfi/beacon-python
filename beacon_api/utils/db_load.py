import os
import csv
import argparse
import json

import asyncio
import asyncpg

from ..conf.config import DB_URL
from .logging import LOG

'''--BEACON DATABASE POPULATOR--'''


class BeaconDB:
    """Database connection and operations."""

    def __init__(self, db_url):
        """Start database routines."""
        LOG.info('Start database routines')
        try:
            LOG.info('Fetch database URL')
            self._db_url = db_url
        except Exception as e:
            LOG.error(f'ERROR CONSTRUCTING DSN: {e}')
        else:
            LOG.info(f'Database URL has been set -> Connections can now be made')

    async def connection(self):
        """Connect to the database."""
        LOG.info('Establish a connection to database')
        try:
            self._conn = await asyncpg.connect(self._db_url)
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO CONNECT TO DATABASE -> {e}')
        else:
            LOG.info(f'Database connection has been established')

    async def check_tables(self, desired_tables):
        """Check that correct tables exist in the database."""
        LOG.info('Request tables from database')
        found_tables = []
        tables = await self._conn.fetch('SELECT table_name '
                                        'FROM information_schema.tables '
                                        'WHERE table_schema=\'public\' '
                                        'AND table_type=\'BASE TABLE\';')
        LOG.info('Tables received -> check that correct tables exist')
        for table in list(tables):
            found_tables.append(dict(table)['table_name'])
        missing_tables = list(set(desired_tables)-set(found_tables))
        for table in found_tables:
            LOG.info(f'{table} exists')
        for table in missing_tables:
            LOG.error(f'{table} is missing!')
        return missing_tables

    async def create_tables(self, sql_file):
        """Create tables to database according to given schema."""
        LOG.info(f'Create tables to database according to given schema in file {sql_file}')
        try:
            with open(sql_file, 'r') as file:
                schema = file.read()
            await self._conn.execute(schema)
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO CREATE TABLES -> {e}')
        else:
            LOG.info('Tables have been created')

    async def load_metadata(self, metafile):
        """Parse metadata from a JSON file and insert it into the database."""
        try:
            LOG.info(f'Parsing metadata from {metafile}')
            with open(metafile, 'r') as file:
                metadata = json.load(file)
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO PARSE METADATA FROM {metafile} -> {e}')
        else:
            LOG.info('Metadata has been parsed')
            try:
                LOG.info(f'Attempting to insert metadata to database')
                await self._conn.execute('INSERT INTO beacon_dataset_table '
                                        '(name, description, assemblyid, '
                                        'createdatetime, updatedatetime, '
                                        'version, variantcount, callcount, '
                                        'samplecount, externalurl, accesstype) '
                                        'VALUES '
                                        '($1, $2, $3, NOW(), NOW(), '
                                        '$4, $5, $6, $7, $8, $9)',
                                        metadata['name'], metadata['description'],
                                        metadata['assemblyId'], metadata['version'],
                                        metadata['variantCount'], metadata['callCount'],
                                        metadata['sampleCount'], metadata['externalUrl'],
                                        metadata['accessType'])
            except Exception as e:
                LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO INSERT METADATA INTO THE DATABASE -> {e}')
            else:
                LOG.info(f'Metadata for {metafile} inserted succesffully')

    async def load_datafile(self, datafile):
        """Insert variant data to the database."""
        LOG.info(f'Load variants from file {datafile}')
        queue = []
        with open(datafile, 'r') as file:
            data = csv.reader(file, delimiter=';')
            for datum in data:
                queue.append(datum)
        # Insert items from queue in one session and commit all cases at once
        async with self._conn.transaction():
            LOG.info('Insert variants into the database')
            for item in queue:
                await self._conn.execute('INSERT INTO beacon_data_table '
                                         '(dataset_id, start, chromosome, reference, alternate, '
                                         '"end", type, sv_length, variantcount, callcount, samplecount, frequency) '
                                         'VALUES '
                                         '($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)',
                                         item[0], int(item[1]), item[2], item[3], item[4], int(0 if item[5] == '' else item[5]),
                                         item[6], int(0 if item[7] == '' else item[7]), int(item[8]), int(item[9]), int(item[10]),
                                         float(item[11]))

    async def close(self):
        """Close the database connection."""
        try:
            LOG.info('Mark the database connection to be closed')
            await self._conn.close()
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO CLOSE DATABASE CONNECTION -> {e}')
        else:
            LOG.info('The database connection has been closed')


async def init_beacon_db(arguments=None):
    """Run database operations here."""
    # Fetch command line arguments
    args = parse_arguments(arguments)

    # Initialise the database connection
    db = BeaconDB(DB_URL)

    # Connect to the database
    await db.connection()

    # Check that desired tables exist (missing tables are returned)
    tables = await db.check_tables(['beacon_dataset_table', 'beacon_data_table'])

    # If some tables are missing, run init.sql to recover them
    if len(tables) > 0:
        await db.create_tables(os.environ.get('TABLES_SCHEMA', 'data/init.sql'))

    # Insert dataset metadata into the database, prior to inserting actual variant data
    await db.load_metadata(args.metadata)

    # Insert data into the database
    await db.load_datafile(args.datafile)

    # Close the database connection
    await db.close()


def parse_arguments(arguments):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Load datafiles with associated metadata '
                                     'into the beacon database. See example data and metadata files '
                                     'in the /data directory')
    parser.add_argument('datafile',
                        help='.csv file containing variant information')
    parser.add_argument('metadata',
                        help='.json file containing metadata associated to datafile')
    return parser.parse_args(arguments)


def main():
    """Run the magic."""
    # TO DO add this to setup to run from command line
    # allow arguments to be passed from command line
    asyncio.get_event_loop().run_until_complete(init_beacon_db())
    # TO DO Python3.7 will become that
    # maybe we should move to 3.7
    # asyncio.run(main())


if __name__ == "__main__":
    main()

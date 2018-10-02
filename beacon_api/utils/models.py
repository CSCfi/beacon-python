import os
import logging
import csv

import asyncio
import asyncpg

from ..conf.config import DB_URL

'''--ASYNCHRONOUS POSTGRES OPERATIONS--'''

# CONFIGURE LOGGING
FORMAT = '[%(asctime)s][%(name)s][%(process)d %(processName)s][%(levelname)-8s] (L:%(lineno)s) %(funcName)s: %(message)s'
logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class BeaconDB:
    """Database connection and operations."""

    def __init__(self, db_url):
        """Start database routines."""
        LOG.info('Start database routines')
        try:
            LOG.info('Construct DSN for database connection')
            self._db_url = db_url
        except Exception as e:
            LOG.error(f'ERROR CONSTRUCTING DSN: {e}')
        else:
            LOG.info(f'DSN has been constructed -> Connections can now be made')

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

    async def load_dataset(self, name, description, assembly_id, version, variant_count, call_count, sample_count, external_url, access_type):
        """Insert dataset information to the database."""
        try:
            LOG.info(f'Attempting to insert {name} metadata to database')
            await self._conn.execute('INSERT INTO beacon_dataset_table '
                                     '(name, description, assemblyid, '
                                     'createdatetime, updatedatetime, '
                                     'version, variantcount, callcount, '
                                     'samplecount, externalurl, accesstype) '
                                     'VALUES '
                                     '($1, $2, $3, NOW(), NOW(), '
                                     '$4, $5, $6, $7, $8, $9)',
                                     name, description, assembly_id, version,
                                     variant_count, call_count, sample_count,
                                     external_url, access_type)
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO INSERT METADATA INTO THE DATABASE -> {e}')
        else:
            LOG.info(f'Metadata for {name} inserted succesffully')

    async def load_variants(self, datafile):
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


async def main():
    """Run database operations here."""
    # Initialise the database connection
    db = BeaconDB(DB_URL)

    # Connect to the database
    await db.connection()

    # Check that desired tables exist (missing tables are returned)
    tables = await db.check_tables(['beacon_dataset_table', 'beacon_data_table'])

    # If some tables are missing, run init.sql
    if len(tables) > 0:
        await db.create_tables(os.environ.get('TABLES_SCHEMA', 'init.sql'))

    # Insert dataset metadata into the database, prior to inserting actual variant data
    await db.load_dataset(name='DATASET1',
                          description='example dataset number 1',
                          assembly_id='GRCh38',
                          version='v1',
                          variant_count=6966,
                          call_count=360576,
                          sample_count=1,
                          external_url='externalUrl',
                          access_type='PUBLIC')
    await db.load_dataset(name='DATASET2',
                          description='example dataset number 2',
                          assembly_id='GRCh38',
                          version='v1',
                          variant_count=16023,
                          call_count=445712,
                          sample_count=1,
                          external_url='externalUrl',
                          access_type='PUBLIC')
    await db.load_dataset(name='DATASET3',
                          description='example dataset number 3',
                          assembly_id='GRCh38',
                          version='v1',
                          variant_count=20952,
                          call_count=1206928,
                          sample_count=1,
                          external_url='externalUrl',
                          access_type='PUBLIC')

    # Insert data into the database
    await db.load_variants('data/dataset1.csv')
    await db.load_variants('data/dataset2.csv')
    await db.load_variants('data/dataset3.csv')

    # Close the database connection
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())

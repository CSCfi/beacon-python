"""Beacon Database Loader.

This utility script is used to parse VCF files into a PostgreSQL database.
See :ref:`database` table ``beacon_data_table`` for what information is extracted from the VCF file.

Datafiles ``*.vcf`` are denoted as ``datafile`` in the script parameters.
Metadata for a datafile is given in a ``*.json`` file, denoted as ``metafile`` in the script parameters.

.. note:: Future releases are expected to drop the additional ``metafile``
        parameter in favour of simplifying the database loading process,
        reading metadata from the datafile(s) directly.


Environment Setup
-----------------

Location of the table creation script can be changed with the ``TABLES_SCHEMA`` environment variable.

+---------------------+------------------------+---------------------------------------------------+
| ENV                 | Default                | Description                                       |
+---------------------+------------------------+---------------------------------------------------+
| `TABLES_SCHEMA`     | `data/init.sql`        | Database tables schema for metadata and variants. |
+---------------------+------------------------+---------------------------------------------------+

Run Module
----------

Below are the two ways of running this module (pip installed and uninstalled).

.. code-block:: console

    $ beacon_init [datafile] [metafile]
    $ python -m beacon_api.utils.db_load [datafile] [metafile]


.. note:: This script has been tested with VCF specification v4.2.
"""

import os
import argparse
import json
import itertools

import asyncio
import asyncpg
from cyvcf2 import VCF

from datetime import datetime

from .logging import LOG


class BeaconDB:
    """Database connection and operations."""

    def __init__(self):
        """Start database routines."""
        LOG.info('Start database routines')
        self._conn = None

    def _transform_vt(self, vt, variant):
        """Transform variant types."""
        if vt in ['s', 'snp']:
            return 'SNP'
        elif vt in ['m', 'mnp']:
            return 'MNP'
        elif vt in ['i', 'indel']:
            return 'INS' if len(variant.ALT) > len(variant.REF) else 'DEL'
        else:
            LOG.debug(f'Other variantType value {variant.var_type.upper()}')
            return variant.var_type.upper()

    def _handle_type(self, value, type):
        """Determine if values are in a tuple and also convert them to specific type."""
        ar = []
        if isinstance(value, tuple):
            ar = [type(i) for i in value]
        elif isinstance(value, type):
            ar = [type(value)]

        return ar

    def _rchop(self, thestring, ending):
        """Chop SV type if any SV is in the ``me_type`` list.

        If a ``SV=LINE1`` is not supported thus we meed to used the ALT base
        ``INS:ME:LINE1`` but removing the ``:LINE1`` from the end.

        .. warning:: This data transformation might only be valid for 1000genome.
        """
        if thestring.endswith(ending):
            return thestring[:-len(ending)]
        return thestring

    def _unpack(self, variant, len_samples):
        """Unpack variant type, allele frequency and count."""
        aaf = []
        ac = []
        vt = []
        alt = variant.ALT
        me_type = ['dup:tandem', 'del:me', 'ins:me']
        # sv_type = ['dup', 'inv', 'ins', 'del', 'cnv']
        # supported_vt = ['snp', 'indel', 'mnp', 'dup', 'inv', 'ins', 'del']
        for k, v in variant.INFO:
            if k == 'AC':
                ac = self._handle_type(v, int)
            if k == 'AN':
                an = v
            else:
                an = variant.num_called*2
            if k == 'AF':
                aaf = self._handle_type(v, float)
            else:
                aaf = [float(ac_value) / float(an) for ac_value in ac]
            if variant.is_sv:
                alt = [elem.strip("<>") for elem in variant.ALT]
                if k == 'SVTYPE':
                    vt = [self._rchop(e, ":"+v) if e.lower().startswith(tuple(me_type)) else v for e in alt]
            else:
                if k == 'VT':
                    vt = [self._transform_vt(var_type.lower(), variant) for var_type in v.split(',')]

        return (aaf, ac, vt, alt, an)

    async def connection(self):
        """Connect to the database."""
        LOG.info('Establish a connection to database')
        try:
            self._conn = await asyncpg.connect(host=os.environ.get('DATABASE_URL', 'localhost'),
                                               port=os.environ.get('DATABASE_PORT', '5432'),
                                               user=os.environ.get('DATABASE_USER', 'beacon'),
                                               password=os.environ.get('DATABASE_PASSWORD', 'beacon'),
                                               database=os.environ.get('DATABASE_NAME', 'beacondb'))
            LOG.info('Database connection has been established')
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO CONNECT TO DATABASE -> {e}')

    async def check_tables(self, desired_tables):
        """Check that correct tables exist in the database."""
        LOG.info('Request tables from database')
        found_tables = []
        tables = await self._conn.fetch("""SELECT table_name
                                        FROM information_schema.tables
                                        WHERE table_schema='public'
                                        AND table_type='BASE TABLE';""")
        LOG.info('Tables received -> check that correct tables exist')
        for table in list(tables):
            found_tables.append(dict(table)['table_name'])
        missing_tables = list(set(desired_tables) - set(found_tables))
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
            LOG.info('Tables have been created')
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO CREATE TABLES -> {e}')

    async def load_metadata(self, vcf, metafile, datafile):
        """Parse metadata from a JSON file and insert it into the database."""
        metadata = {}
        try:
            LOG.info(f'Calculate number of samples from {datafile}')
            len_samples = len(vcf.samples)
            LOG.info(f'Parse metadata from {metafile}')
            with open(metafile, 'r') as metafile:
                # read metadata from given JSON file
                # TO DO: parse metadata directly from datafile if possible
                LOG.info(metafile)
                metadata = json.load(metafile)
            LOG.info(metadata)
            LOG.info('Metadata has been parsed')
            try:
                LOG.info(f'Attempting to insert metadata to database')
                await self._conn.execute("""INSERT INTO beacon_dataset_table
                                         (name, datasetId, description, assemblyId,
                                         createDateTime, updateDateTime, version,
                                         sampleCount, externalUrl, accessType)
                                         VALUES
                                         ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                                         ON CONFLICT (name, datasetId)
                                         DO NOTHING""",
                                         metadata['name'], metadata['datasetId'],
                                         metadata['description'], metadata['assemblyId'],
                                         datetime.strptime(metadata['createDateTime'], '%Y-%m-%d %H:%M:%S'),
                                         datetime.strptime(metadata['updateDateTime'], '%Y-%m-%d %H:%M:%S'),
                                         metadata['version'], len_samples,
                                         metadata['externalUrl'], metadata['accessType'])
                await self._conn.execute("""INSERT INTO beacon_dataset_counts_table
                                         (datasetId, callCount, variantCount)
                                         VALUES
                                         ($1, $2, $3)""",
                                         metadata['datasetId'], metadata['callCount'],
                                         metadata['variantCount'])
            except Exception as e:
                LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO INSERT METADATA -> {e}')
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO PARSE METADATA -> {e}')
        return metadata['datasetId']

    def _chunks(self, iterable, size):
        """Generate record.

        Encountered at: https://stackoverflow.com/a/24527424/10143238
        """
        iterator = iter(iterable)
        for first in iterator:
            yield itertools.chain([first], itertools.islice(iterator, size - 1))

    async def load_datafile(self, vcf, datafile, dataset_id, n=1000):
        """Parse data from datafile and send it to be inserted."""
        LOG.info(f'Read data from {datafile}')
        len_samples = len(vcf.samples)
        try:
            LOG.info('Generate database queue(s)')
            data = self._chunks(vcf, n)
            for record in data:
                await self.insert_variants(dataset_id, list(record), len_samples)
            LOG.info(f'{datafile} has been processed')
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE GENERATING DB QUEUE -> {e}')

    async def insert_variants(self, dataset_id, variants, len_samples):
        """Insert variant data to the database."""
        LOG.info(f'Received {len(variants)} variants for insertion to {dataset_id}')
        try:
            # Insertions are committed when transaction is closed
            async with self._conn.transaction():
                LOG.info('Insert variants into the database')
                for variant in variants:
                    # params = (frequency, count, actual variant Type)
                    if variant.aaf > 0:
                        params = self._unpack(variant, len_samples)
                        # Coordinates that are read from VCF are 1-based, cyvcf2 reads them as 0-based, and they are inserted into the DB as such
                        await self._conn.execute("""INSERT INTO beacon_data_table
                                                 (datasetId, chromosome, start, reference, alternate,
                                                 "end", aggregatedVariantType, alleleCount, callCount, frequency, variantType)
                                                 SELECT ($1), ($2), ($3), ($4), t.alt, ($6), ($7), t.ac, ($9), t.freq, t.vt
                                                 FROM (SELECT unnest($5::varchar[]) alt, unnest($8::integer[]) ac,
                                                 unnest($10::float[]) freq, unnest($11::varchar[]) as vt) t
                                                 ON CONFLICT (datasetId, chromosome, start, reference, alternate)
                                                 DO NOTHING""",
                                                 dataset_id, variant.CHROM, variant.start, variant.REF,
                                                 params[3], variant.end, variant.var_type.upper(),
                                                 params[1], params[4], params[0], params[2])
                        LOG.debug('Variants have been inserted')
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO INSERT VARIANTS -> {e}')

    async def close(self):
        """Close the database connection."""
        try:
            LOG.info('Mark the database connection to be closed')
            await self._conn.close()
            LOG.info('The database connection has been closed')
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO CLOSE DATABASE CONNECTION -> {e}')


async def init_beacon_db(arguments=None):
    """Run database operations here."""
    # Fetch command line arguments
    args = parse_arguments(arguments)

    # Initialise the database connection
    db = BeaconDB()

    # Connect to the database
    await db.connection()

    # Get sample list if it's set
    vcf = VCF(args.datafile, samples=args.samples.split(',') if args.samples else None)

    # Check that desired tables exist (missing tables are returned)
    tables = await db.check_tables(['beacon_dataset_table', 'beacon_data_table', 'beacon_dataset_counts_table'])

    # If some tables are missing, run init.sql to recover them
    if len(tables) > 0:
        await db.create_tables(os.environ.get('TABLES_SCHEMA', 'data/init.sql'))

    # Insert dataset metadata into the database, prior to inserting actual variant data
    dataset_id = await db.load_metadata(vcf, args.metadata, args.datafile)

    # Insert data into the database
    await db.load_datafile(vcf, args.datafile, dataset_id)

    # Close the database connection
    await db.close()


def parse_arguments(arguments):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="""Load datafiles with associated metadata
                                     into the beacon database. See example data and metadata files
                                     in the /data directory.""")
    parser.add_argument('datafile',
                        help='.vcf file containing variant information')
    parser.add_argument('metadata',
                        help='.json file containing metadata associated to datafile')
    parser.add_argument('--samples', default=None,
                        help='comma separated string of samples to process')
    return parser.parse_args(arguments)


def main():
    """Run the beacon_init script."""
    # TO DO add this to setup to run from command line
    # allow arguments to be passed from command line
    asyncio.get_event_loop().run_until_complete(init_beacon_db())
    # TO DO Python3.7 will become that
    # maybe we should move to 3.7
    # asyncio.run(main())


if __name__ == "__main__":
    main()

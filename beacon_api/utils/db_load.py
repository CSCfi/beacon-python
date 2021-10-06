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
import sys
import argparse
import ujson
import itertools
import re

import asyncio
import asyncpg
from cyvcf2 import VCF

from pathlib import Path
from datetime import datetime

from .logging import LOG


class BeaconDB:
    """Database connection and operations."""

    def __init__(self) -> None:
        """Start database routines."""
        LOG.info("Start database routines")
        self._conn = None

    def _alt_length_check(self, variant, i, default):
        """Figure out if the Alternate base is longer than the Reference base."""
        if len(variant.ALT[i]) > len(variant.REF):
            return "INS"
        elif len(variant.ALT[i]) == len(variant.REF):
            return default
        else:
            return "DEL"

    def _transform_vt(self, vt, variant, i):
        """Transform variant types."""
        if vt in ["s", "snp"]:
            return self._alt_length_check(variant, i, "SNP")
        elif vt in ["m", "mnp"]:
            return self._alt_length_check(variant, i, "MNP")
        elif vt in ["i", "indel"]:
            return self._alt_length_check(variant, i, "SNP")
        else:
            return variant.var_type.upper()

    def _handle_type(self, value, type):
        """Determine if values are in a tuple and also convert them to specific type."""
        ar = []
        if isinstance(value, tuple):
            ar = [type(i) for i in value]
        elif isinstance(value, type):
            ar = [type(value)]

        return ar

    def _bnd_parts(self, alt, mate):
        """Retrieve BND SV type parts.

        We retrieve more than needed
        """
        # REF ALT  Meaning
        # s   t[p[ piece extending to the right of p is joined after t
        # s   t]p] reverse comp piece extending left of p is joined after t
        # s   ]p]t piece extending to the left of p is joined before t
        # s   [p[t reverse comp piece extending right of p is joined before t
        # where p is chr:pos
        patt = re.compile("[\\[\\]]")
        mate_items = patt.split(alt)
        remoteCoords = mate_items[1].split(":")
        chr = remoteCoords[0].lower()
        if chr[0] == "<":
            chr = chr[1:-1]
            withinMainAssembly = False
        else:
            withinMainAssembly = True
        pos = int(remoteCoords[1])
        orientation = alt[0] == "[" or alt[0] == "]"
        remoteOrientation = re.search("\\[", alt) is not None
        if orientation:
            connectingSequence = mate_items[2]
        else:
            connectingSequence = mate_items[0]

        return (chr, pos, orientation, remoteOrientation, connectingSequence, withinMainAssembly, mate)

    def _rchop(self, thestring, ending):
        """Chop SV type if any SV is in the ``me_type`` list.

        The ``SV=LINE1`` is not supported, thus we meed to used the ALT base
        ``INS:ME:LINE1`` but removing the ``:LINE1`` from the end.

        .. warning:: This data transformation might only be valid for 1000genome.
        """
        if thestring.endswith(ending):
            return thestring[: -len(ending)]
        return thestring

    def _unpack(self, variant):
        """Unpack variant type, allele frequency and count.

        This is quite a complicated parser, but it is custom made to address some of
        expectations regarding the data to be delivered by the beacon API.

        .. warning:: By no means this is exahustive in processing of VCF Records.
        """
        aaf = []
        ac = []
        vt = []
        bnd = []
        alt = variant.ALT
        me_type = ["dup:tandem", "del:me", "ins:me"]

        ac = self._handle_type(variant.INFO.get("AC"), int) if variant.INFO.get("AC") else []
        an = variant.INFO.get("AN") if variant.INFO.get("AN") else variant.num_called * 2
        if variant.INFO.get("AF"):
            aaf = self._handle_type(variant.INFO.get("AF"), float)
        else:
            aaf = [float(ac_value) / float(an) for ac_value in ac]

        if variant.is_sv:
            alt = [elem.strip("<>") for elem in variant.ALT]
            if variant.INFO.get("SVTYPE"):
                v = variant.INFO.get("SVTYPE")
                if v == "BND":
                    bnd = [self._bnd_parts(e, variant.INFO.get("MATEID")) for e in alt]
                    vt = ["BND" for e in alt]
                else:
                    vt = [self._rchop(e, ":" + v) if e.lower().startswith(tuple(me_type)) else v for e in alt]
        else:
            if variant.INFO.get("VT"):
                v = variant.INFO.get("VT").split(",")
                if len(alt) > len(v):
                    vt_temp = [[self._transform_vt(var_type.lower(), variant, i) for i, k in enumerate(alt)] for var_type in v]
                    vt = vt_temp[0]
                else:
                    vt = [self._transform_vt(var_type.lower(), variant, i) for i, var_type in enumerate(v)]

        return (aaf, ac, vt, alt, an, bnd)

    async def connection(self):
        """Connect to the database."""
        LOG.info("Establish a connection to database")
        try:
            self._conn = await asyncpg.connect(
                host=os.environ.get("DATABASE_URL", "localhost"),
                port=os.environ.get("DATABASE_PORT", "5432"),
                user=os.environ.get("DATABASE_USER", "beacon"),
                password=os.environ.get("DATABASE_PASSWORD", "beacon"),
                database=os.environ.get("DATABASE_NAME", "beacondb"),
            )
            LOG.info("Database connection has been established")
        except Exception as e:
            LOG.error(f"AN ERROR OCCURRED WHILE ATTEMPTING TO CONNECT TO DATABASE -> {e}")

    async def check_tables(self, desired_tables):
        """Check that correct tables exist in the database."""
        LOG.info("Request tables from database")
        found_tables = []
        tables = await self._conn.fetch(
            """SELECT table_name
                                        FROM information_schema.tables
                                        WHERE table_schema='public'
                                        AND table_type='BASE TABLE';"""
        )
        LOG.info("Tables received -> check that correct tables exist")
        for table in list(tables):
            found_tables.append(dict(table)["table_name"])
        missing_tables = list(set(desired_tables) - set(found_tables))
        for table in found_tables:
            LOG.info(f"{table} exists")
        for table in missing_tables:
            LOG.error(f"{table} is missing!")
        return missing_tables

    async def create_tables(self, sql_file):
        """Create tables to database according to given schema."""
        LOG.info(f"Create tables to database according to given schema in file {sql_file}")
        try:
            with open(sql_file, "r") as file:
                schema = file.read()
            await self._conn.execute(schema)
            LOG.info("Tables have been created")
        except Exception as e:
            LOG.error(f"AN ERROR OCCURRED WHILE ATTEMPTING TO CREATE TABLES -> {e}")

    async def load_metadata(self, vcf, metafile, datafile):
        """Parse metadata from a JSON file and insert it into the database."""
        metadata = {}
        try:
            LOG.info(f"Calculate number of samples from {datafile}")
            len_samples = len(vcf.samples)
            LOG.info(f"Parse metadata from {metafile}")
            with open(metafile, "r") as meta_file:
                # read metadata from given JSON file
                # TO DO: parse metadata directly from datafile if possible
                LOG.info(meta_file)
                metadata = ujson.load(meta_file)
            LOG.info(metadata)
            LOG.info("Metadata has been parsed")
            try:
                LOG.info("Attempting to insert metadata to database")
                await self._conn.execute(
                    """INSERT INTO beacon_dataset_table
                                         (name, datasetId, description, assemblyId,
                                         createDateTime, updateDateTime, version,
                                         sampleCount, externalUrl, accessType)
                                         VALUES
                                         ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                                         ON CONFLICT (name, datasetId)
                                         DO NOTHING""",
                    metadata["name"],
                    metadata["datasetId"],
                    metadata["description"],
                    metadata["assemblyId"],
                    datetime.strptime(metadata["createDateTime"], "%Y-%m-%d %H:%M:%S"),
                    datetime.strptime(metadata["updateDateTime"], "%Y-%m-%d %H:%M:%S"),
                    metadata["version"],
                    len_samples,
                    metadata["externalUrl"],
                    metadata["accessType"],
                )
                await self._conn.execute(
                    """INSERT INTO beacon_dataset_counts_table
                                         (datasetId, callCount, variantCount)
                                         VALUES
                                         ($1, $2, $3)""",
                    metadata["datasetId"],
                    metadata["callCount"],
                    metadata["variantCount"],
                )
            except Exception as e:
                LOG.error(f"AN ERROR OCCURRED WHILE ATTEMPTING TO INSERT METADATA -> {e}")
        except Exception as e:
            LOG.error(f"AN ERROR OCCURRED WHILE ATTEMPTING TO PARSE METADATA -> {e}")
        else:
            return metadata["datasetId"]

    def _chunks(self, iterable, size):
        """Chunk records.

        Encountered at: https://stackoverflow.com/a/24527424/10143238
        """
        iterator = iter(iterable)
        for first in iterator:
            yield itertools.chain([first], itertools.islice(iterator, size - 1))

    async def load_datafile(self, vcf, datafile, dataset_id, n=1000, min_ac=1):
        """Parse data from datafile and send it to be inserted."""
        LOG.info(f"Read data from {datafile}")
        try:
            LOG.info("Generate database queue(s)")
            data = self._chunks(vcf, n)
            for record in data:
                await self.insert_variants(dataset_id, list(record), min_ac)
            LOG.info(f"{datafile} has been processed")
        except Exception as e:
            LOG.error(f"AN ERROR OCCURRED WHILE GENERATING DB QUEUE -> {e}")

    async def insert_variants(self, dataset_id, variants, min_ac):
        """Insert variant data to the database."""
        LOG.info(f"Received {len(variants)} variants for insertion to {dataset_id}")
        try:
            # Insertions are committed when transaction is closed
            async with self._conn.transaction():
                LOG.info("Insert variants into the database")
                for variant in variants:
                    # params = (frequency, count, actual variant Type)
                    params = self._unpack(variant)
                    # Coordinates that are read from VCF are 1-based,
                    # cyvcf2 reads them as 0-based, and they are inserted into the DB as such

                    # params may carry single variants [1] or packed variants [20, 15, 10, 1]
                    # The first check prunes for single variants, packed variants must be removed afterwards
                    if params[1][0] >= min_ac:
                        # Remove packed variants that don't meet the minimum allele count requirements
                        # Packed variants are always ordered from largest to smallest, this process starts
                        # popping values from the right (small) side until there are no more small values to pop
                        while params[1][-1] < min_ac:
                            params[0].pop()  # aaf
                            params[1].pop()  # ac
                            params[2].pop()  # vt
                            params[3].pop()  # alt
                            if len(params[5]) > 0:
                                params[5].pop()  # bnd

                        # Nothing interesting on the variant with no aaf
                        # because none of the samples have it
                        if variant.aaf > 0:

                            # We Process Breakend Records into a different table for now
                            if params[5] != []:
                                # await self.insert_mates(dataset_id, variant, params)
                                # Most likely there will be only one BND per Record
                                for bnd in params[5]:
                                    await self._conn.execute(
                                        """INSERT INTO beacon_mate_table
                                                            (datasetId, chromosome, chromosomeStart, chromosomePos,
                                                            mate, mateStart, matePos, reference, alternate, alleleCount,
                                                            callCount, frequency, "end")
                                                            SELECT ($1), ($2), ($3), ($4),
                                                            ($5), ($6), ($7), ($8), t.alt, t.ac, ($11), t.freq, ($13)
                                                            FROM (SELECT unnest($9::varchar[]) alt, unnest($10::integer[]) ac,
                                                            unnest($12::float[]) freq) t
                                                            ON CONFLICT (datasetId, chromosome, mate, chromosomePos, matePos)
                                                            DO NOTHING""",
                                        dataset_id,
                                        variant.CHROM.replace("chr", ""),
                                        variant.start,
                                        variant.ID,
                                        bnd[0].replace("chr", ""),
                                        bnd[1],
                                        bnd[6],
                                        variant.REF,
                                        params[3],
                                        params[1],
                                        params[4],
                                        params[0],
                                        variant.end,
                                    )
                            else:
                                await self._conn.execute(
                                    """INSERT INTO beacon_data_table
                                                        (datasetId, chromosome, start, reference, alternate,
                                                        "end", aggregatedVariantType, alleleCount, callCount, frequency, variantType)
                                                        SELECT ($1), ($2), ($3), ($4), t.alt, ($6), ($7), t.ac, ($9), t.freq, t.vt
                                                        FROM (SELECT unnest($5::varchar[]) alt, unnest($8::integer[]) ac,
                                                        unnest($10::float[]) freq, unnest($11::varchar[]) as vt) t
                                                        ON CONFLICT (datasetId, chromosome, start, reference, alternate)
                                                        DO NOTHING""",
                                    dataset_id,
                                    variant.CHROM.replace("chr", ""),
                                    variant.start,
                                    variant.REF,
                                    params[3],
                                    variant.end,
                                    variant.var_type.upper(),
                                    params[1],
                                    params[4],
                                    params[0],
                                    params[2],
                                )

                            LOG.debug("Variants have been inserted")
        except Exception as e:
            LOG.error(f"AN ERROR OCCURRED WHILE ATTEMPTING TO INSERT VARIANTS -> {e}")

    async def close(self):
        """Close the database connection."""
        try:
            LOG.info("Mark the database connection to be closed")
            await self._conn.close()
            LOG.info("The database connection has been closed")
        except Exception as e:
            LOG.error(f"AN ERROR OCCURRED WHILE ATTEMPTING TO CLOSE DATABASE CONNECTION -> {e}")


async def init_beacon_db(arguments=None):
    """Run database operations here."""
    # Fetch command line arguments
    args = parse_arguments(arguments)
    validate_arguments(args)

    # Initialise the database connection
    db = BeaconDB()

    # Connect to the database
    await db.connection()

    # Get sample list if it's set
    vcf = VCF(args.datafile, samples=args.samples.split(",") if args.samples else None)

    # Check that desired tables exist (missing tables are returned)
    tables = await db.check_tables(["beacon_dataset_table", "beacon_data_table", "beacon_dataset_counts_table"])

    # If some tables are missing, run init.sql to recover them
    if len(tables) > 0:
        await db.create_tables(os.environ.get("TABLES_SCHEMA", "data/init.sql"))

    # Insert dataset metadata into the database, prior to inserting actual variant data
    dataset_id = await db.load_metadata(vcf, args.metadata, args.datafile)

    # Insert data into the database
    await db.load_datafile(vcf, args.datafile, dataset_id, min_ac=int(args.min_allele_count))

    # Close the database connection
    await db.close()


def validate_arguments(arguments):
    """Check that given arguments are valid."""
    if not Path(arguments.datafile).is_file():
        sys.exit(f"Could not find datafile: {arguments.datafile}")
    if not Path(arguments.metadata).is_file():
        sys.exit(f"Could not find metadata file: {arguments.metadata}")
    if not arguments.min_allele_count.isdigit():
        sys.exit(f"Minimum allele count --min_allele_count must be a positive integer, received: {arguments.min_allele_count}")


def parse_arguments(arguments):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="""Load datafiles with associated metadata
                                     into the beacon database. See example data and metadata files
                                     in the /data directory."""
    )
    parser.add_argument("datafile", help=".vcf file containing variant information")
    parser.add_argument("metadata", help=".json file containing metadata associated to datafile")
    parser.add_argument("--samples", default=None, help="comma separated string of samples to process. EXPERIMENTAL")
    parser.add_argument("--min_allele_count", default="1", help="minimum allele count can be raised to ignore rare variants. Default value is 1")
    return parser.parse_args(arguments)


def main():
    """Run the beacon_init script."""
    # TO DO add this to setup to run from command line
    # allow arguments to be passed from command line
    if sys.version_info >= (3, 7):
        asyncio.run(init_beacon_db())
    else:
        asyncio.get_event_loop().run_until_complete(init_beacon_db())


if __name__ == "__main__":
    main()

Instructions
============

.. note:: In order to run ``beacon-python`` Web Server requirements are as specified below:

  * Python 3.6+;
  * running DB `PostgreSQL Server <https://www.postgresql.org/>`_  9.6+.


Environment Setup
-----------------

The application requires some environmental arguments in order to run properly, these are illustrated in
the table below.

+---------------------+-------------------------------+--------------------------------------------------+
| ENV                 | Default                       | Description                                      |
+---------------------+-------------------------------+--------------------------------------------------+
| `DATABASE_URL`      | `postgresql://localhost:5432` | The URL for the PostgreSQL server.               |
+---------------------+-------------------------------+--------------------------------------------------+
| `DATABASE_NAME`     | `beacondb`                    | Name of the database.                            |
+---------------------+-------------------------------+--------------------------------------------------+
| `DATABASE_USER`     | `beacon`                      | Database username.                               |
+---------------------+-------------------------------+--------------------------------------------------+
| `DATABASE_PASSWORD` | `beacon`                      | Database password.                               |
+---------------------+-------------------------------+--------------------------------------------------+
| `HOST`              | `0.0.0.0`                     | Default Host for the Web Server.                 |
+---------------------+-------------------------------+--------------------------------------------------+
| `PORT`              | `5050`                        | Default port for the Web Server.                 |
+---------------------+-------------------------------+--------------------------------------------------+
| `DEBUG`             | `True`                        | If set to `True`, Standard Output.               |
+---------------------+-------------------------------+--------------------------------------------------+
| `PUBLIC_KEY`        | `\n`                          | Public key, armored, for validating the token.   |
+---------------------+-------------------------------+--------------------------------------------------+

Setting the necessary environment variables can be done  e.g. via the command line:

.. code-block:: console

    $ export DATABASE_URL=postgresql://localhost:5432
    $ export DATABASE_NAME=beacondb
    $ export DATABASE_USER=beacon
    $ export DATABASE_PASSWORD=beacon
    $ export HOST=0.0.0.0
    $ export PORT=5050
    $ export DEBUG=True
    $ export PUBLIC_KEY=armored_key

.. _app-setup:

beacon-python Setup
-------------------

For installing `beacon-python` do the following:

.. code-block:: console

    $ git clone https://github.com/CSCfi/beacon-python
    $ pip install -r requirements.txt
    $ cd beacon-python
    $ pip install .

Before running the application proceed with the :ref:`database-setup`.

.. code-block:: console

    $ beacon

.. _database-setup:

Database Setup
--------------

Full information about the database schema and the queries performed against it
see: :ref:`database`.

Starting PostgreSQL using Docker:

.. code-block:: console

    cd beacon-python
    docker run -e POSTGRES_USER=beacon \
               -e POSTGRES_PASSWORD=beacon \
               -e POSTGRES_DB=beacondb \
               -v "$PWD/data":/docker-entrypoint-initdb.d
               -p 5432:5432 postgres:9.6

For loading example database we provide the ``beacon_init`` utility:

.. code-block:: console

    ╰─$ beacon_init --help
    usage: beacon_init [-h] datafile metadata

    Load datafiles with associated metadata into the beacon database. See example
    data and metadata files in the /data directory.

    positional arguments:
      datafile    .vcf file containing variant information
      metadata    .json file containing metadata associated to datafile

    optional arguments:
      -h, --help  show this help message and exit

Dataset metadata format is as follows:

.. code-block:: javascript

    {
    "name": "ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf",
    "datasetId": "urn:hg:exampleid",
    "description": "Mitochondrial genome from the 1000 Genomes project",
    "assemblyId": "GRCh38",
    "createDateTime": "2013-05-02 12:00:00",
    "updateDateTime": "2013-05-02 12:00:00",
    "version": "v0.4",
    "externalUrl": "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf.gz",
    "accessType": "PUBLIC"
    }

For loading data into the database we can proceed as follows:

.. code-block:: console

    $ wget ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf.gz
    $ beacon_init ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf.gz data/example_metadata.json

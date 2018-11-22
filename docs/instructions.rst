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
| `CONFIG_FILE`       | `./beacon_api/conf/config.ini`| Provide specific :ref:`beacon-info`.             |
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

.. _beacon-info:

Beacon Information
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # This file is used to configure the Beacon info endpoint
    # This file's default location is /beacon-python/beacon_api/conf/config.ini
    [beacon_general_info]
    # Name of the Beacon service
    title=EGA Beacon
    # Version of the Beacon implementation
    version=1.0.0
    # Author of this software
    author=CSC developers
    # Software license for this distribution
    license=Apache 2.0
    # Copyright holder for this software
    copyright=CSC - IT Center for Science
    [beacon_api_info]
    # Version of the Beacon API specification this implementation adheres to
    apiVersion=1.0.0
    # Globally unique identifier for this Beacon instance
    beaconId=elixir-finland
    # Description of this Beacon service
    description=Beacon API Web Server based on the GA4GH Beacon API
    # Homepage for Beacon service
    url=https://ega-archive.org/
    # Alternative URL for Beacon service for e.g. internal use cases
    alturl=https://ega-archive.org/
    # Datetime when this Beacon was created
    createtime=2018-07-25T00:00:00Z
    [organisation_info]
    # Globally unique identifier for organisation that hosts this Beacon service
    org_id=CSC
    # Name of organisation that hosts this Beacon service
    org_name=CSC - IT Center for Science
    # Description for organisation
    org_description=Finnish expertise in ICT for research, education, culture and public administration
    # Visit address of organisation
    org_address=Keilaranta 14, Espoo, finland
    # Homepage of organisation
    org_welcomeUrl=https://www.csc.fi/
    # URL for contacting organisation
    org_contactUrl=https://www.csc.fi/contact-info
    # URL for organisation logo
    org_logoUrl=https://www.csc.fi/documents/10180/161914/CSC_2012_LOGO_RGB_72dpi.jpg
    # Other organisational information
    org_info=CSC represents Finland in the ELIXIR partner nodes


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

To run the application from command line use:

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

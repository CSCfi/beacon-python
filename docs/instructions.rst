Instructions
============

.. note:: In order to run ``beacon-python`` Web Server requirements are as specified below:

  * Python 3.6+;
  * running DB `PostgreSQL Server <https://www.postgresql.org/>`_  9.6+.

.. _env-setup:

Environment Setup
-----------------

The application requires some environmental arguments in order to run properly, these are illustrated in
the table below.

+---------------------+-------------------------------+--------------------------------------------------+
| ENV                 | Default                       | Description                                      |
+---------------------+-------------------------------+--------------------------------------------------+
| `DATABASE_URL`      | `localhost`                   | The URL for the PostgreSQL server.               |
+---------------------+-------------------------------+--------------------------------------------------+
| `DATABASE_PORT`     | `5432`                        | The port for the PostgreSQL server.              |
+---------------------+-------------------------------+--------------------------------------------------+
| `DATABASE_NAME`     | `beacondb`                    | Name of the database.                            |
+---------------------+-------------------------------+--------------------------------------------------+
| `DATABASE_USER`     | `beacon`                      | Database username.                               |
+---------------------+-------------------------------+--------------------------------------------------+
| `DATABASE_PASSWORD` | `beacon`                      | Database password.                               |
+---------------------+-------------------------------+--------------------------------------------------+
| `DATABASE_SCHEMA`   | `-`                           | Database Schema if one is used.                  |
+---------------------+-------------------------------+--------------------------------------------------+
| `HOST`              | `0.0.0.0`                     | Default Host for the Web Server.                 |
+---------------------+-------------------------------+--------------------------------------------------+
| `PORT`              | `5050`                        | Default port for the Web Server.                 |
+---------------------+-------------------------------+--------------------------------------------------+
| `DEBUG`             | `True`                        | If set to `True`, Standard Output.               |
+---------------------+-------------------------------+--------------------------------------------------+
| `PUBLIC_KEY`        | `-`                           | Public key, armored, for validating the token.   |
+---------------------+-------------------------------+--------------------------------------------------+
| `CONFIG_FILE`       | `./beacon_api/conf/config.ini`| Provide specific :ref:`beacon-info`.             |
+---------------------+-------------------------------+--------------------------------------------------+
| `TABLES_SCHEMA`     | `data/init.sql`               | Provide ``beacon_init`` SQL fallback schema.     |
+---------------------+-------------------------------+--------------------------------------------------+

Setting the necessary environment variables can be done  e.g. via the command line:

.. code-block:: console

    $ export DATABASE_URL=localhost
    $ export DATABASE_PORT=5434
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

By default the beacon contains preset information about the beacon service.
The information can be changed in a configuration file that has the structure specified below, by
pointing to the location of the file using `CONFIG_FILE` environment variable.

.. literalinclude:: /../beacon_api/conf/config.ini
   :language: python
   :lines: 1-65

.. _oauth2:

OAuth2 Configuration
~~~~~~~~~~~~~~~~~~~~

Beacon utilises OAuth2 (JWT) Bearer tokens to authenticate users when they are accessing registered datasets.
The configuration variables reside in the same `CONFIG_FILE` as described above in the ``oauth2`` section.

.. literalinclude:: /../beacon_api/conf/config.ini
   :language: python
   :lines: 68-76

``server`` should point to an API that returns a public key which can be used to validate the received Bearer token.
``issuers`` is a string of comma separated values, e.g. `one,two,three` without spaces. The issuers string contains
a list of entities that are viewed as trusted organisations.
``bona_fide`` should point to an API that returns the `bona_fide_status` for now
`ELIXIR <https://www.elixir-europe.org/services/compute/aai>`_ specific.

.. note:: For implementing `CONTROLLED` dataset permissions see :ref:`permissions`.


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

Gunicorn Setup
~~~~~~~~~~~~~~

By default the application will run a simple aiohttp web server, and best solution in most cases.
For other options see `aiohttp Server Deployment <https://aiohttp.readthedocs.io/en/stable/deployment.html>`_
we recommend ``gunicorn``.

.. code-block:: console

    $ gunicorn beacon_api.app:init --bind $THE_HOST:$THE_PORT \
                                   --worker-class aiohttp.GunicornUVLoopWebWorker \
                                   --workers 4

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
      --samples   comma separated string of samples to process
      -h, --help  show this help message and exit

Dataset metadata format is as follows:

.. code-block:: javascript

    {
        "name": "1000 genomoe",
        "datasetId": "urn:hg:1000genome",
        "description": "Data from 1000 genome project",
        "assemblyId": "GRCh38",
        "createDateTime": "2013-05-02 12:00:00",
        "updateDateTime": "2013-05-02 12:00:00",
        "version": "v0.4",
        "externalUrl": "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/",
        "accessType": "PUBLIC"
    }


For loading data into the database we can proceed as follows:

.. code-block:: console

    $ beacon_init data/ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf.gz data/example_metadata.json

For loading data into the database from selected samples only we can proceed as follows:

.. code-block:: console

    $ beacon_init data/ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf.gz data/example_metadata.json --samples HG0001,HG0002,HG0003

.. note:: One dataset can have multiple files, in order to add more files to one dataset, repeat the command above.

.. note:: For loading 1000 genome dataset see: :ref:`genome-dataset` instructions.

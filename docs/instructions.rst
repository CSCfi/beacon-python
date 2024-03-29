Instructions
============

.. note:: In order to run ``beacon-python`` Web Server requirements are as specified below:

  * Python 3.10+;
  * running DB `PostgreSQL Server <https://www.postgresql.org/>`_  9.6+ (recommended 13).

.. _env-setup:

Environment Setup
-----------------

The application requires some environmental arguments in order to run properly, these are illustrated in
the table below.

+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| ENV                 | Default                       | Description                                                                 |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| `DATABASE_URL`      | `localhost`                   | The URL for the PostgreSQL server.                                          |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| `DATABASE_PORT`     | `5432`                        | The port for the PostgreSQL server.                                         |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| `DATABASE_NAME`     | `beacondb`                    | Name of the database.                                                       |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| `DATABASE_USER`     | `beacon`                      | Database username.                                                          |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| `DATABASE_PASSWORD` | `beacon`                      | Database password.                                                          |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| `DATABASE_SCHEMA`   | `-`                           | Database Schema if used. Comma separated if multiple used.                  |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| `HOST`              | `0.0.0.0`                     | Default Host for the Web Server.                                            |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| `PORT`              | `5050`                        | Default port for the Web Server.                                            |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| `DEBUG`             | `True`                        | If set to `True`, Standard Output.                                          |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| `PUBLIC_KEY`        | `-`                           | Public key, armored, for validating the token.                              |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| `CONFIG_FILE`       | `./beacon_api/conf/config.ini`| Provide specific :ref:`beacon-info`.                                        |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| `TABLES_SCHEMA`     | `data/init.sql`               | Provide ``beacon_init`` SQL fallback schema.                                |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+
| `JWT_AUD`           |                               | JWT audiences. Overwrites the ``audience`` variable in configuration file.  |
+---------------------+-------------------------------+-----------------------------------------------------------------------------+

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

By default the beacon contains information about the beacon service.
The information can be changed in a configuration file that has the structure specified below, or by
pointing to the location of the file using `CONFIG_FILE` environment variable.

.. literalinclude:: /../beacon_api/conf/config.ini
   :language: python
   :lines: 1-76

.. _oauth2:

OAuth2 Configuration
~~~~~~~~~~~~~~~~~~~~

Beacon utilises OAuth2 (JWT) Bearer tokens to authenticate users when they are accessing registered datasets.
The configuration variables reside in the same `CONFIG_FILE` as described above in the ``oauth2`` section.

.. literalinclude:: /../beacon_api/conf/config.ini
   :language: python
   :lines: 98-124

* ``server`` should point to an API that returns a public key, which can be used to validate the received JWTBearer token.
* ``issuers`` is a string of comma separated values, e.g. `one,two,three` without spaces. The issuers string should contain
  a list of entities that are viewed as trusted organisations.
* ``bona_fide`` should point to an API that returns the `bona_fide_status` this is
  `ELIXIR AAI <https://www.elixir-europe.org/services/compute/aai>`_ specific.
* ``audience`` is a string of comma separated values, e.g. ``aud1,aud2,aud3`` of intended audiences. Audience is a value
  in JWT that describes what service(s) the token is intended for.

The audience `hash` or `URI` from the AAI service can be used, or if the service is part of a `Beacon Network`,
use the key provided by the Beacon Network administrator.

**Leave empty if the service doesn't care about the intended audience.**

``verify_aud`` can be set to either ``True`` or ``False``. If enabled, this option forces Beacon to verify the audience(s)
in the supplied token. If disabled, the audience(s) of a token will not be validated.

Disabling this can be a good solution for standalone
Beacons, that want to be able to use tokens generated by any authority. If ``verify_aud=True`` is set
provide also value(s) for ``audience`` key, as otherwise the audience will be attempted to be validated, but as no audiences
are listed, the validation will fail.

.. note:: For implementing `CONTROLLED` dataset permissions see :ref:`permissions`.


.. _app-setup:

beacon-python Setup
-------------------

For installing ``beacon-python`` do the following:

.. code-block:: console

    $ git clone https://github.com/CSCfi/beacon-python
    $ pip install -r requirements.txt
    $ cd beacon-python
    $ pip install .

.. hint:: Before running the application:

          * configure information related to your beacon in :ref:`beacon-info`;
          * proceed with the :ref:`database-setup`.

To run the application from command line use:

.. code-block:: console

    $ beacon

For advance setup see `Gunicorn Setup` below.

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
is available at: :ref:`database`.

Starting PostgreSQL using Docker:

.. code-block:: console

    cd beacon-python
    docker run -d \
               -e POSTGRES_USER=beacon \
               -e POSTGRES_PASSWORD=beacon \
               -e POSTGRES_DB=beacondb \
               -v "$PWD/data":/docker-entrypoint-initdb.d \
               -p 5432:5432 postgres:13

.. hint:: If one has their own database the ``beacon_init`` utility can be skipped,
          and make use of their own database by:

          * creating a DB View that matches the DB schema for the beacon python server see: :ref:`database`
            for information on the database schema and queries;
          * migrating the database to match the :ref:`database` schema;
          * modifying the queries in :meth:`beacon_api.utils.data_query` in order to fit one's own database.


Loading data (Optional)
~~~~~~~~~~~~~~~~~~~~~~~

For loading datasets to database we provide the ``beacon_init`` utility:

.. code-block:: console

    $ beacon_init --help
    usage: beacon_init [-h] [--samples SAMPLES]
                      [--min_allele_count MIN_ALLELE_COUNT]
                      datafile metadata

    Load datafiles with associated metadata into the beacon database. See example
    data and metadata files in the /data directory.

    positional arguments:
      datafile              .vcf file containing variant information
      metadata              .json file containing metadata associated to datafile

    optional arguments:
      -h, --help            show this help message and exit
      --samples SAMPLES     comma separated string of samples to process.
                            EXPERIMENTAL
      --min_allele_count MIN_ALLELE_COUNT
                            minimum allele count can be raised to ignore rare
                            variants. Default value is 1

As an example, a dataset metadata could be:

.. code-block:: javascript

    {
        "name": "1000 genome",
        "datasetId": "urn:hg:1000genome",
        "description": "Data from 1000 genome project",
        "assemblyId": "GRCh38",
        "createDateTime": "2013-05-02 12:00:00",
        "updateDateTime": "2013-05-02 12:00:00",
        "version": "v0.4",
        "externalUrl": "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/",
        "accessType": "PUBLIC",
        "callCount": 3892,
        "variantCount": 4242
    }


For loading data into the database we can proceed as follows:

.. code-block:: console

    $ beacon_init data/ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf.gz data/example_metadata.json

(EXPERIMENTAL) For loading data into the database from selected samples only we can proceed as follows:

.. code-block:: console

    $ beacon_init data/ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf.gz data/example_metadata.json --samples HG0001,HG0002,HG0003

For ignoring rare alleles, set a minimum allele count with ``--min_allele_count``:

.. code-block:: console

    $ beacon_init data/ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf.gz data/example_metadata.json --min_allele_count 20

.. note:: One dataset can have multiple files, in order to add more files to one dataset, repeat the command above.
          The parameters ``callCount`` and ``variantCount`` from the metadata file reflect values of the entire dataset.
          These values can be initialised with ``0`` if they are not known and updated in ``beacon_dataset_counts_table`` table.
          As of this moment we do not provide an option for bulk upload of files from a dataset.

.. note:: For loading 1000 genome dataset see: :ref:`genome-dataset` instructions.

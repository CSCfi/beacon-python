Instructions
============

.. note:: In order to run ``beacon-python`` Web Server requirements are as specified below:

  * Python 3.6+;
  * running DB `PostgreSQL Server <https://www.postgresql.org/>`_  9.6+.

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

Setting the necessary environment variables can be done  e.g. via the command line:

.. code-block:: console

    $ export DATABASE_URL=postgresql://localhost:5432
    $ export DATABASE_NAME=beacondb
    $ export DATABASE_USER=beacon
    $ export DATABASE_PASSWORD=beacon
    $ export HOST=0.0.0.0
    $ export PORT=5050
    $ export DEBUG=True

Starting PostgreSQL using Docker:

.. code-block:: console

    docker run -e POSTGRES_USER=beacon \
               -e POSTGRES_PASSWORD=beacon \
               -e POSTGRES_DB=beacondb \
               -p 5432:5432 postgres:9.6

For loading example database we provide the ``beacon_init`` utility:

.. code-block:: console

    ╰─$ beacon_init --help
    usage: beacon_init [-h] datafile metadata

    Load datafiles with associated metadata into the beacon database. See example
    data and metadata files in the /data directory.

    positional arguments:
      datafile    .csv file containing variant information.
      metadata    .json file containing metadata associated to datafile.

    optional arguments:
      -h, --help  show this help message and exit

Load example data from the ``/data`` folder, as follows:

.. code-block:: console

    $ beacon_init data/dataset1.csv data/dataset1_metadata.json
    $ beacon_init data/dataset2.csv data/dataset2_metadata.json
    $ beacon_init data/dataset3.csv data/dataset3_metadata.json

## beacon-python - Python-based Beacon API Web Server

[![Build Status](https://travis-ci.org/CSCfi/beacon-python.svg?branch=master)](https://travis-ci.org/CSCfi/beacon-python)
[![Coverage Status](https://coveralls.io/repos/github/CSCfi/beacon-python/badge.svg?branch=master)](https://coveralls.io/github/CSCfi/beacon-python?branch=master)
[![Documentation Status](https://readthedocs.org/projects/beacon-python/badge/?version=latest)](https://beacon-python.readthedocs.io/en/latest/?badge=latest)

Documentation: https://beacon-python.readthedocs.io

### Quick start

`beacon-python` Web Server requires:
* Python 3.6+;
* running DB [PostgreSQL Server](https://www.postgresql.org/) 9.6+.

```shell
git clone https://github.com/CSCfi/beacon-python
pip install -r requirements.txt
cd beacon-python
```

#### Database start

Start the PostgreSQL DB server and set up `POSTGRES_USER` and `POSTGRES_PASSWORD` as `beacon` and `POSTGRES_DB` as `beacondb` (default values, that can be changed via environment variables - see [documentation](https://beacon-python.readthedocs.io) for instructions).

Recommended is to start PostgreSQL using [Docker](https://www.docker.com/):

```shell
docker run -e POSTGRES_USER=beacon \
           -e POSTGRES_PASSWORD=beacon \
           -v "$PWD/data":/docker-entrypoint-initdb.d
           -e POSTGRES_DB=beacondb \
           -p 5432:5432 postgres:9.6
```

#### Run beacon-python

For installing `beacon-python` do the following:

```shell
pip install .
```

If one has their own database the ``beacon_init`` utility can be skipped, and make use of their own database by:
* creating a DB View that matches the DB schema for the beacon python server see: [Database](https://beacon-python.readthedocs.io/en/latest/db.html) documentation for information on the database schema and queries;
* migrate the database to match the [Database](https://beacon-python.readthedocs.io/en/latest/db.html) schema;
* keep own database, but modify the queries in [beacon_api.utils.data_query.py](beacon_api/utils/data_query.py).

For loading `*.vcf`/`*.vcf.gz` files into the database we provide the `beacon_init` utility:
```shell
╰─$ beacon_init --help             
usage: beacon_init [-h] datafile metadata

Load datafiles with associated metadata into the beacon database. See example
data and metadata files in the /data directory.

positional arguments:
  datafile    .vcf file containing variant information
  metadata    .json file containing metadata associated to datafile

optional arguments:
  -h, --help  show this help message and exit
```

Run the `beacon-python` Web Server from the command line simply using:
```shell
beacon
```

### Using the application

The API has two endpoints, the info endpoint `/` and the query end point `/query`. The info end point
gives the user general info about the Beacon and it's datasets, while the query end point allows to
retrieve dataset information based on specific parameters.

For information about the endpoints and parameters consult the [Beacon API specification](https://github.com/ga4gh-beacon/specification/blob/develop/beacon.md)

#### Info endpoint

Request:
- URL: `/`
- HTTP method: `GET`
- Parameters: `None`

#### Query endpoint

Request:
- URL: `/query`
- HTTP method: `GET` and `POST`
- Parameters: Refer to [Beacon API specification](https://github.com/ga4gh-beacon/specification/blob/develop/beacon.md) for full list of parameters.

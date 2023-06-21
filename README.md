## beacon-python - Python-based Beacon API Web Server

![Integration Tests](https://github.com/CSCfi/beacon-python/workflows/Integration%20Tests/badge.svg)
![Python Unit Tests](https://github.com/CSCfi/beacon-python/workflows/Python%20Unit%20Tests/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/CSCfi/beacon-python/badge.svg?branch=HEAD)](https://coveralls.io/github/CSCfi/beacon-python?branch=HEAD)
[![Documentation Status](https://readthedocs.org/projects/beacon-python/badge/?version=latest)](https://beacon-python.readthedocs.io/en/latest/?badge=latest)

Documentation: https://beacon-python.readthedocs.io

### Quick start

`beacon-python` Web Server requires:
* Python 3.10+;
* running DB [PostgreSQL Server](https://www.postgresql.org/) 9.6+ (recommended 13).

```shell
git clone https://github.com/CSCfi/beacon-python
pip install -r requirements.txt
cd beacon-python
```

#### Database start

Start the PostgreSQL DB server and set up `POSTGRES_USER` and `POSTGRES_PASSWORD` as `beacon` and `POSTGRES_DB` as `beacondb` (default values, that can be changed via environment variables - see [documentation](https://beacon-python.readthedocs.io) for instructions).

It is recommended to start PostgreSQL using [Docker](https://www.docker.com/):

```shell
docker run -e POSTGRES_USER=beacon \
           -e POSTGRES_PASSWORD=beacon \
           -v "$PWD/data":/docker-entrypoint-initdb.d \
           -e POSTGRES_DB=beacondb \
           -p 5432:5432 postgres:13
```

#### Run beacon-python

For installing `beacon-python` do the following:

```shell
pip install .
```

#### Loading Data

If one has their own database the ``beacon_init`` utility can be skipped, and make use of the existing database by:
* creating a DB View that matches the DB schema for the beacon python server see: [Database](https://beacon-python.readthedocs.io/en/latest/db.html) documentation for information on the database schema and queries;
* migrating the database to match the [Database](https://beacon-python.readthedocs.io/en/latest/db.html) schema;
* modifying the queries in [beacon_api.utils.data_query.py](beacon_api/utils/data_query.py) in order to fit one's own database.

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

The API has three endpoints, the info endpoint `/`, a second info endpoint `/service-info` for GA4GH compliancy, and the query end point `/query`. The info end point
gives the user general info about the Beacon and it's datasets, while the query end point allows to
retrieve dataset information based on specific parameters. The GA4GH info endpoint serves a minimal data payload.

For information about the endpoints and parameters consult the [Beacon API specification](https://github.com/ga4gh-beacon/specification/blob/develop/beacon.md)

#### Info endpoint

Request:
- URL: `/`
- HTTP method: `GET`
- Parameters: `None`

#### GA4GH Info endpoint

Request:
- URL: `/service-info`
- HTTP method: `GET`
- Parameters: `None`

#### Query endpoint

Request:
- URL: `/query`
- HTTP method: `GET` and `POST`
- Parameters: Refer to [Beacon API specification](https://github.com/ga4gh-beacon/specification/blob/develop/beacon.md) for full list of parameters.

### License

`beacon-python` and all it sources are released under `Apache License 2.0`.

### Acknowledgements

We would like to acknowledge the valuable feedback from the members of [NBIS](https://nbis.se/) and [DDBJ](https://www.ddbj.nig.ac.jp), whose ideas and contributions have helped to make the Beacon services more robust.

# beacon-python
[Beacon API specifications](https://github.com/ga4gh-beacon/specification/blob/release-1.0.0/beacon.md)


## Quick start
...

## Configure database
...

### Create database

The application is using the object relational mapper (ORM) SQLAlchemy to handle much of the communication 
between the application and the database, and that is why the database tables are created using SQLAlchemy.
So instead of manually creating the Postgresql tables using `psql` in the command line, the tables are 
created by calling the `db.create_all` method that uses the `db` object from SQLAlchemy. To call the method we 
use the Python shell in the command line. 


Open the Python shell in the command line:
```commandline
$ python3
```
Create the tables:
```python
>>> from app import db
>>> db.create_all()
``` 

This will create the database tables according to the schema specified in `models.py`.

### Load data

In this example we will fill the `genomes` table first, the order you fill the tables in does not matter
because the tables does not have any direct relations. In the example we load three datasets to the database.

The table needs in the first column the `id`, witch is a number starting from one and iterates with +1 for every row.
If the datasets you are loading dont have this `id` in the first row you can add it the following way.

```commandline
$ awk '{printf "%s;%s\n", NR,$0}' dataset1.csv > dataset1_.csv
$ awk '{printf "%s;%s\n", NR+72,$0}' dataset2.csv > dataset2_.csv
$ awk '{printf "%s;%s\n", NR+161,$0}' dataset3.csv > dataset3_.csv
```

The table column `dataset_id` is the name of the table. If the file that you are loading doesent have the right name in 
that column you can change it using:

```commandline
$ awk -F';' 'BEGIN{OFS=";"}{$2="DATASET1”;print $0}' dataset1_.csv > set1.csv
$ awk -F';' 'BEGIN{OFS=";"}{$2="DATASET2”;print $0}' dataset2_.csv > set2.csv
$ awk -F';' 'BEGIN{OFS=";"}{$2="DATASET3”;print $0}' dataset3_.csv > set3.csv
```

Then we load the `genomes` table with the files. Open `psql` in the command line:

```commandline
$ psql beacondb
```
Copy the files into the table:

```sql
beacondb=# COPY genomes FROM '/opt/app-root/files/set1.csv' DELIMITER ';' CSV;
beacondb=# COPY genomes FROM '/opt/app-root/files/set2.csv' DELIMITER ';' CSV;
beacondb=# COPY genomes FROM '/opt/app-root/files/set3.csv' DELIMITER ';' CSV;
```

Then we check for the right values to fill in the beacon_dataset_table in the variantCount and callCount:

````commandline
$ awk -F ';' '{SUM+=$10}END{print SUM}' set1.csv			#variantCount
$ awk -F ';' '{SUM+=$11}END{print SUM}' set1.csv			#callCount
````
variantCount = 6966, callCount = 360576 for set1.csv
```commandline
$ awk -F ';' '{SUM+=$10}END{print SUM}' set2.csv			#variantCount
$ awk -F ';' '{SUM+=$11}END{print SUM}' set2.csv			#callCount
```
variantCount = 16023, callCount = 445712 for set2.csv
```commandline
$ awk -F ';' '{SUM+=$10}END{print SUM}' set3.csv			#variantCount
$ awk -F ';' '{SUM+=$11}END{print SUM}' set3.csv			#callCount
```
variantCount = 20952, callCount = 1206928 for set3.csv


Lastly we fill the `beacon_dataset_table` with the right info for the different datasets. You can 
either fill it using the method `load_dataset_table()` in `models.py`, or by using `psql` from the 
command line.

Using `load_dataset_table()`in python shell:
```python
from models import load_dataset_table

load_dataset_table('DATASET1', 'example dataset number 1', 'GRCh38', 'v1', 6966, 360576, 1, 'externalUrl', 'PUBLIC')
load_dataset_table('DATASET2', 'example dataset number 2', 'GRCh38', 'v1', 16023, 445712, 1, 'externalUrl', 'PUBLIC')
load_dataset_table('DATASET3', 'example dataset number 3', 'GRCh38', 'v1', 20952, 1206928, 1, 'externalUrl', 'PUBLIC')
```

Using `psql` in command line:
```sql
INSERT INTO beacon_dataset_table (name, description, assemblyId, createDateTime, updateDateTime, version, variantCount, callCount, sampleCount, externalUrl, accessType) VALUES ('DATASET1', 'example dataset number 1', 'GRCh38', 'v1', 6966, 360576, 1, 'externalUrl', 'PUBLIC');

INSERT INTO beacon_dataset_table (name, description, assemblyId, createDateTime, updateDateTime, version, variantCount, callCount, sampleCount, externalUrl, accessType) VALUES ('DATASET2', 'example dataset number 2', 'GRCh38', 'v1', 16023, 445712, 1, 'externalUrl', 'PUBLIC');

INSERT INTO beacon_dataset_table (name, description, assemblyId, createDateTime, updateDateTime, version, variantCount, callCount, sampleCount, externalUrl, accessType) VALUES ('DATASET2', 'example dataset number 2', 'GRCh38', 'v1', 20952, 1206928, 1, 'externalUrl', 'PUBLIC');
```


You can also fill the `genomes` table using the `load_data_table()` function aswell. This function 
will fill in the `id` automatically so then you shouldn't use a file where you have added the `id` numbers.

```python
from models import load_data_table

load_data_table('set1.csv')
load_data_table('set2.csv')
load_data_table('set3.csv')
```

## Using the application

The API has two endpoints, the info endpoint `/` and the query end point `/query`. The info end point 
gives the user general info about the Beacon and it's datasets, while the query end point 

### Info endpoint

#### Request 
###### - URL: `/`
###### - HTTP method: `GET`
###### - Parameters: `None`

#### Response
###### Content-type:`application/json`
###### Payload: `Beacon object`

#### Examples 
An example `GET` request and response to the info endpoint:    
    
    > GET / HTTP/1.1
    > Host: localhost:5000
    > User-Agent: curl/7.54.0
    > Accept: */*
    > 
    * HTTP 1.0, assume close after body
    < HTTP/1.0 200 OK
    < Content-Type: application/json
    < Content-Length: 2391
    < Server: Werkzeug/0.14.1 Python/3.6.5
    < Date: Fri, 08 Jun 2018 12:07:36 GMT
    < 
    {
      "alternativeUrl": "https://ega-archive.org/beacon_web/", 
      "apiVersion": "0.4", 
      "createDateTime": "2015-06-15T00:00.000Z", 
      "dataset": [
        {
          "assemblyId": "grch37", 
          "callCount": 74, 
          "description": "This sample set comprises cases of schizophrenia with additional cognitive measurements, collected in Aberdeen, Scotland.", 
          "id": "EGAD00000000028", 
          "info": {}, 
          "sampleCount": 1, 
          "variantCount": 74, 
        }
      ], 
      "description": "This <a href=\"http://ga4gh.org/#/beacon\">Beacon</a> is based on the GA4GH Beacon <a href=\"https://github.com/ga4gh/beacon-team/blob/develop/src/main/resources/avro/beacon.avdl\">API 0.4</a>", 
      "id": "ega-beacon", 
      "info": {
        "size": "60270153"
      }, 
      "name": "EGA Beacon", 
      "organization": {
        "address": "", 
        "contactUrl": "mailto:beacon.ega@crg.eu", 
        "description": "The European Genome-phenome Archive (EGA) is a service for permanent archiving and sharing of all types of personally identifiable genetic and phenotypic data resulting from biomedical research projects.", 
        "id": "EGA", 
        "logoUrl": "https://ega-archive.org/images/logo.png", 
        "name": "European Genome-Phenome Archive (EGA)", 
        "welcomeUrl": "https://ega-archive.org/"
      }, 
      "sampleAlleleRequests": [
        {
          "alternateBases": "A", 
          "assemblyId": "GRCh37", 
          "includeDatasetResponses": false, 
          "referenceBases": "C", 
          "referenceName": "17", 
          "start": 6689
        }, 
        {
          "alternateBases": "G", 
          "assemblyId": "GRCh37", 
          "datasetIds": [
            "EGAD00000000028"
          ], 
          "includeDatasetResponses": "ALL", 
          "referenceBases": "A", 
          "referenceName": "1", 
          "start": 14929
        }, 
        {
          "alternateBases": "CCCCT", 
          "assemblyId": "GRCh37", 
          "datasetIds": [
            "EGAD00001000740", 
            "EGAD00001000741"
          ], 
          "includeDatasetResponses": "HIT", 
          "referenceBases": "C", 
          "referenceName": "1", 
          "start": 866510
        }
      ], 
      "version": "v04", 
      "welcomeUrl": "https://ega-archive.org/beacon_web/"
    }
    * Closing connection 0

### Query endpoint

#### Request
###### - URL: `/query`
###### - HTTP method: `GET`, `POST`
###### - Content-Type: `application/x-www-form-urlencoded`(POST)
###### - Parameters: `BeaconAlleleRequest`

#### Response
###### Content-type:`application/json`
###### Payload: `Beacon Allele Response object`


#### Examples

Example of how to use the GET method in the `/query` endpoint:

```commandline
$ curl -v 'http://localhost:5000/query?referenceName=1&start=0&end=0&startMin=28000000&startMax=29000000&endMin=28000000&endMax=29000000&referenceBases=A&alternateBases=T&assemblyId=GRCh37&datasetIds=EGAD00000000028&includeDatasetResponses=ALL'
```
    
######
    
```commandline
> GET /query?referenceName=1&start=0&end=0&startMin=28000000&startMax=29000000&endMin=28000000&endMax=29000000&referenceBases=A&alternateBases=T&assemblyId=GRCh37&datasetIds=EGAD00000000028&includeDatasetResponses=ALL HTTP/1.1
> Host: localhost:5000
> User-Agent: curl/7.54.0
> Accept: */*
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Type: application/json
< Content-Length: 1078
< Server: Werkzeug/0.14.1 Python/3.6.5
< Date: Mon, 11 Jun 2018 07:29:26 GMT
< 
{
    "beaconId": "ega-beacon",
    "apiVersion": "0.4",
    "exists": true,
    "error": null,
    "alleleRequest": {
        "referenceName": "1",
        "start": 0,
        "startMin": 28000000,
        "startMax": 29000000,
        "end": 0,
        "endMin": 28000000,
        "endMax": 29000000,
        "referenceBases": "A",
        "alternateBases": "T",
        "assemblyId": "GRCh37",
        "datasetIds": [
            "EGAD00000000028"
        ],
        "includeDatasetResponses": "ALL"
    },
    "datasetAlleleResponses": [
        {
            "datasetId": "EGAD00000000028",
            "exists": true,
            "frequency": 0.5,
            "variantCount": 1,
            "callCount": 1,
            "sampleCount": 1,
            "note": "This sample set comprises cases of schizophrenia with additional cognitive measurements, collected in Aberdeen, Scotland.",
            "externalUrl": null,
            "info": {},
            "error": null
        }
    ]
}
* Closing connection 0    
```
    
######
Example of how to use the POST method in the "/query" path:
   
```commandline
$ curl -v -d "referenceName=1&start=14929&referenceBases=A&alternateBases=G&assemblyId=GRCh37&datasetIds=EGAD00000000028&includeDatsetResponses=ALL" http://localhost:5000/query
```
    
    
```commandline
> POST /query HTTP/1.1
> Host: localhost:5000
> User-Agent: curl/7.54.0
> Accept: */*
> Content-Length: 133
> Content-Type: application/x-www-form-urlencoded
> 
* upload completely sent off: 133 out of 133 bytes
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Type: application/json
< Content-Length: 1056
< Server: Werkzeug/0.14.1 Python/3.6.5
< Date: Mon, 11 Jun 2018 07:15:48 GMT
< 
{
    "beaconId": "ega-beacon",
    "apiVersion": "0.4",
    "exists": true,
    "error": null,
    "alleleRequest": {
        "referenceName": "1",
        "start": 14929,
        "startMin": 0,
        "startMax": 0,
        "end": 0,
        "endMin": 0,
        "endMax": 0,
        "referenceBases": "A",
        "alternateBases": "G",
        "assemblyId": "GRCh37",
        "datasetIds": [
            "EGAD00000000028"
        ],
        "includeDatasetResponses": "ALL"
    },
    "datasetAlleleResponses": [
        {
            "datasetId": "EGAD00000000028",
            "exists": true,
            "frequency": 0.5,
            "variantCount": 1,
            "callCount": 1,
            "sampleCount": 1,
            "note": "This sample set comprises cases of schizophrenia with additional cognitive measurements, collected in Aberdeen, Scotland.",
            "externalUrl": null,
            "info": {},
            "error": null
        }
    ]
}
* Closing connection 0
```

```commandline
$ curl -v 'http://localhost:5000/query?&start=0&end=0&startMin=28000000&startMax=29000000&endMin=28000000&endMax=29000000&referenceBases=A&alternateBases=T&assemblyId=GRCh37&datasetIds=EGAD00000000028&includeDatasetResponses=ALL'`
```


```commandline
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 5000 (#0)
> GET /query?&start=0&end=0&startMin=28000000&startMax=29000000&endMin=28000000&endMax=29000000&referenceBases=A&alternateBases=T&assemblyId=GRCh37&datasetIds=EGAD00000000028&includeDatasetResponses=ALL HTTP/1.1
> Host: localhost:5000
> User-Agent: curl/7.54.0
> Accept: */*
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 400 BAD REQUEST
< Content-Type: application/json
< Content-Length: 791
< Server: Werkzeug/0.14.1 Python/3.6.5
< Date: Fri, 06 Jul 2018 09:15:39 GMT
< 
{
    "message": {
        "beaconId": "ega-beacon",
        "apiVersion": "0.4",
        "exists": null,
        "error": {
            "errorCode": 400,
            "errorMessage": "Missing mandatory parameter referenceName"
        },
        "allelRequest": {
            "referenceName": "0",
            "start": 0,
            "startMin": 28000000,
            "startMax": 29000000,
            "end": 0,
            "endMin": 28000000,
            "endMax": 29000000,
            "referenceBases": "A",
            "alternateBases": "T",
            "variantType": "0",
            "assemblyId": "GRCh37",
            "datasetIds": [
                "EGAD00000000028"
            ],
            "includeDatasetResponses": "ALL"
        },
        "datasetAlleleResponses": []
    }
}
* Closing connection 0
```

## Further information


### Project structure

```
beacon-python
├─beacon_api
|   ├─beacon_info.py
|   ├─check_functions.py
|   ├─error_handelers.py
|   ├─models.py
|   ├─requirements.txt
|   └─wsgi.py
└─test
    ├─test-expected_outcome-py
    ├─test_get_200.py
    ├─test_get_400.py
    ├─test_get_401.py
    ├─test_post_200.py
    ├─test_post_400.py
    └─test_post_401.py
```

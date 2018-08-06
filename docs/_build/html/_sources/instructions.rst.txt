Example usage
==============

The API has two endpoints, the info endpoint ``/`` and the query end
point ``/query``. The info end point gives the user general info about
the Beacon and it’s datasets, while the query end point

Info endpoint
~~~~~~~~~~~~~

Request
^^^^^^^

- URL: ``/``


- HTTP method: ``GET``


- Parameters: ``None``


Response
^^^^^^^^

Content-type:\ ``application/json``


Payload: ``Beacon object``


Examples
^^^^^^^^

An example ``GET`` request and response to the info endpoint:

.. code:: shell

   $ curl -v 'http://beaconapi-elixirbeacon.rahtiapp.fi/'



   *   Trying 193.167.189.101...
   * TCP_NODELAY set
   * Connected to beaconapi-elixirbeacon.rahtiapp.fi (193.167.189.101) port 80 (#0)
   > GET / HTTP/1.1
   > Host: beaconapi-elixirbeacon.rahtiapp.fi
   > User-Agent: curl/7.54.0
   > Accept: */*
   >
   < HTTP/1.1 200 OK
   < Server: gunicorn/19.9.0
   < Date: Tue, 31 Jul 2018 12:10:53 GMT
   < Content-Type: application/json
   < Content-Length: 2391
   < Set-Cookie: eeadd1720fcd75b91205443a24cfbacf=97f5c3f4c5d9d73de00e92277c49a74f; path=/; HttpOnly
   < Cache-control: private
   <
   {
       "id": "ega-beacon",
       "name": "EGA Beacon",
       "apiVersion": "1.0.0",
       "organization": {
           "id": "EGA",
           "name": "European Genome-Phenome Archive (EGA)",
           "description": "The European Genome-phenome Archive (EGA) is a service for permanent archiving and sharing of all types of personally identifiable genetic and phenotypic data resulting from biomedical research projects.",
           "address": "",
           "welcomeUrl": "https://ega-archive.org/",
           "contactUrl": "mailto:beacon.ega@crg.eu",
           "logoUrl": "https://ega-archive.org/images/logo.png",
           "info": null
       },
       "description": "This <a href=\"http://ga4gh.org/#/beacon\">Beacon</a> is based on the GA4GH Beacon <a href=\"https://github.com/ga4gh/beacon-team/blob/develop/src/main/resources/avro/beacon.avdl\">API 0.4</a>",
       "version": "v1",
       "welcomeUrl": "https://ega-archive.org/beacon_web/",
       "alternativeUrl": "https://ega-archive.org/beacon_web/",
       "createDateTime": "2018-07-25T00:00.000Z",
       "updateDateTime": null,
       "dataset": [
           {
               "id": 1,
               "name": "DATASET1",
               "description": "example dataset number 1",
               "assemblyId": "GRCh38",
               "createDateTime": null,
               "updateDateTime": null,
               "version": null,
               "variantCount": 6966,
               "callCount": 360576,
               "sampleCount": 1,
               "externalUrl": null,
               "info": {
                   "accessType": "PUBLIC"
               }
           },
           {
               "id": 3,
               "name": "DATASET3",
               "description": "example dataset number 3",
               "assemblyId": "GRCh38",
               "createDateTime": null,
               "updateDateTime": null,
               "version": null,
               "variantCount": 20952,
               "callCount": 1206928,
               "sampleCount": 1,
               "externalUrl": null,
               "info": {
                   "accessType": "PUBLIC"
               }
           },
           {
               "id": 2,
               "name": "DATASET2",
               "description": "example dataset number 2",
               "assemblyId": "GRCh38",
               "createDateTime": null,
               "updateDateTime": null,
               "version": null,
               "variantCount": 16023,
               "callCount": 445712,
               "sampleCount": 1,
               "externalUrl": null,
               "info": {
                   "accessType": "REGISTERED"
               }
           }
       ],
       "sampleAlleleRequests": [
           {
               "alternateBases": "A",
               "referenceBases": "C",
               "referenceName": "17",
               "start": 6689,
               "assemblyId": "GRCh37",
               "datasetIds": null,
               "includeDatasetResponses": false
           },
           {
               "alternateBases": "G",
               "referenceBases": "A",
               "referenceName": "1",
               "start": 14929,
               "assemblyId": "GRCh37",
               "datasetIds": [
                   "EGAD00000000028"
               ],
               "includeDatasetResponses": "ALL"
           },
           {
               "alternateBases": "CCCCT",
               "referenceBases": "C",
               "referenceName": "1",
               "start": 866510,
               "assemblyId": "GRCh37",
               "datasetIds": [
                   "EGAD00001000740",
                   "EGAD00001000741"
               ],
               "includeDatasetResponses": "HIT"
           }
       ],
       "info": {
           "size": ""
       }
   }
   * Connection #0 to host beaconapi-elixirbeacon.rahtiapp.fi left intact


Query endpoint
~~~~~~~~~~~~~~

Request
^^^^^^^

- URL: ``/query``


- HTTP method: ``GET``, ``POST``


- Content-Type: ``application/x-www-form-urlencoded``\ (POST)


- Parameters: ``BeaconAlleleRequest``


Response
^^^^^^^^

Content-type:\ ``application/json``


Payload: ``Beacon Allele Response object``


Examples
^^^^^^^^

Example of how to use the GET method in the ``/query`` endpoint:

.. code:: shell

    $ curl -v 'http://beaconapi-elixirbeacon.rahtiapp.fi/query?referenceName=1&start=2947892&referenceBases=A&alternateBases=G&variantType=SNP&assemblyId=GRCh37&includeDatasetResponses=ALL'


    *   Trying 193.167.189.101...
    * TCP_NODELAY set
    * Connected to beaconapi-elixirbeacon.rahtiapp.fi (193.167.189.101) port 80 (#0)
    > GET /query?referenceName=1&start=2947892&referenceBases=A&alternateBases=G&variantType=SNP&assemblyId=GRCh37&includeDatasetResponses=ALL HTTP/1.1
    > Host: beaconapi-elixirbeacon.rahtiapp.fi
    > User-Agent: curl/7.54.0
    > Accept: */*
    >
    < HTTP/1.1 200 OK
    < Server: gunicorn/19.9.0
    < Date: Tue, 31 Jul 2018 12:14:49 GMT
    < Content-Type: application/json
    < Content-Length: 828
    < Set-Cookie: eeadd1720fcd75b91205443a24cfbacf=97f5c3f4c5d9d73de00e92277c49a74f; path=/; HttpOnly
    < Cache-control: private
    <
    {
        "beaconId": "ega-beacon",
        "apiVersion": "1.0.0",
        "exists": true,
        "error": null,
        "allelRequest": {
            "referenceName": "1",
            "start": 2947892,
            "startMin": 0,
            "startMax": 0,
            "end": 0,
            "endMin": 0,
            "endMax": 0,
            "referenceBases": "A",
            "alternateBases": "G",
            "variantType": "SNP",
            "assemblyId": "GRCh37",
            "datasetIds": [],
            "includeDatasetResponses": "ALL"
        },
        "datasetAllelResponses": [
            {
                "datasetId": "DATASET1",
                "exists": true,
                "frequency": 0.0081869,
                "variantCount": 41,
                "callCount": 5008,
                "sampleCount": 2504,
                "note": "example dataset number 1",
                "externalUrl": null,
                "info": {
                    "accessType": "PUBLIC"
                },
                "error": null
            },
            {
                "datasetId": "DATASET3",
                "exists": false,
                "frequency": 0,
                "variantCount": 0,
                "callCount": 0,
                "sampleCount": 0,
                "note": "example dataset number 3",
                "externalUrl": null,
                "info": {
                    "accessType": "PUBLIC"
                },
                "error": null
            }
        ]
    }
    * Connection #0 to host beaconapi-elixirbeacon.rahtiapp.fi left intact

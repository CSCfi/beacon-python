Beacon API Examples
===================

The Beacon API consists of the following endpoints:

* ``/`` beacon information endpoint;
* ``/query`` - retrieving and filtering information from the beacon.

For the full specification consult: `Beacon API specification <https://github.com/ga4gh-beacon/specification>`_.

Info Endpoint
-------------

.. code-block:: console

    $ curl -X GET 'http://localhost:5050/'

Example Response:

.. code-block:: javascript

    {
        "id": "localhost:5050",
        "name": "EGA Beacon",
        "apiVersion": "1.0.0",
        "organization": {
            "id": "EGA",
            "name": "European Genome-Phenome Archive (EGA)",
            "description": "The European Genome-phenome Archive (EGA) is a service for permanent archiving and sharing of all types of personally identifiable         genetic and phenotypic data resulting from biomedical research projects.",
            "address": "",
            "welcomeUrl": "https://ega-archive.org/",
            "contactUrl": "mailto:beacon.ega@crg.eu",
            "logoUrl": "https://ega-archive.org/images/logo.png",
            "info": null
        },
        "description": "This <a href=\"http://ga4gh.org/#/beacon\">Beacon</a> is based on the GA4GH Beacon         <a href=\"https://github.com/ga4gh/beacon-team/blob/develop/src/main/resources/avro/beacon.avdl\">API 0.4</a>",
        "version": "1.0.0",
        "welcomeUrl": "https://ega-archive.org/beacon_web/",
        "alternativeUrl": "https://ega-archive.org/beacon_web/",
        "createDateTime": "2018-07-25T00:00.000Z",
        "updateDateTime": null,
        "dataset": [
            {
                "id": "DATASET2",
                "name": "DATASET2",
                "externalUrl": "https://datasethost.org/dataset2",
                "description": "example dataset number 2",
                "assemblyId": "GRCh38",
                "variantCount": 16023,
                "callCount": 445712,
                "sampleCount": 1,
                "version": "v1",
                "info": [
                    {
                        "accessType": "PUBLIC"
                    }
                ],
                "createDateTime": "2018-10-08T17:31:16Z",
                "updateDateTime": "2018-10-08T17:31:16Z"
            },
            {
                "id": "DATASET3",
                "name": "DATASET3",
                "externalUrl": "https://datasethost.org/dataset3",
                "description": "example dataset number 3",
                "assemblyId": "GRCh38",
                "variantCount": 20952,
                "callCount": 1206928,
                "sampleCount": 1,
                "version": "v1",
                "info": [
                    {
                        "accessType": "REGISTERED"
                    }
                ],
                "createDateTime": "2018-10-08T17:31:21Z",
                "updateDateTime": "2018-10-08T17:31:21Z"
            },
            {
                "id": "DATASET1",
                "name": "DATASET1",
                "externalUrl": "https://datasethost.org/dataset1",
                "description": "example dataset number 1",
                "assemblyId": "GRCh38",
                "variantCount": 6966,
                "callCount": 360576,
                "sampleCount": 2504,
                "version": "v1",
                "info": [
                    {
                        "accessType": "PUBLIC"
                    }
                ],
                "createDateTime": "2018-10-08T17:31:08Z",
                "updateDateTime": "2018-10-08T17:31:08Z"
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
                "includeDatasetResponses": "NONE"
            },
            {
                "alternateBases": "G",
                "referenceBases": "A",
                "referenceName": "1",
                "start": 14929,
                "assemblyId": "GRCh37",
                "datasetIds": [
                    "DATASET1"
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
                    "DATASET2",
                    "DATASET3"
                ],
                "includeDatasetResponses": "HIT"
            }
        ],
        "info": [
            {
                "key": "string",
                "value": "string"
            }
        ]
    }

Query Endpoint
--------------

An example ``GET`` request and response to the ``query`` endpoint:

.. code-block:: console

    $ curl -X GET \
      'http://localhost:5050/query?referenceName=1&referenceBases=C&start=0&assemblyId=GRCh38&alternateBases=T'

Example Response:

.. code-block:: javascript

    {
    "beaconId": "localhost:5050",
    "apiVersion": "1.0.0",
    "exists": true,
    "error": null,
    "alleleRequest": {
        "referenceName": "1",
        "start": 0,
        "startMin": 0,
        "startMax": 0,
        "end": 0,
        "endMin": 0,
        "endMax": 0,
        "referenceBases": "C",
        "assemblyId": "GRCh38",
        "datasetIds": [],
        "includeDatasetResponses": "NONE",
        "alternateBases": "T"
    },
    "datasetAlleleResponses": []
    }


An example ``POST`` request and response to the ``query`` endpoint:

.. code-block:: console

    $ curl -X POST \
      'http://localhost:5050/query' \
      -d '{"referenceName": "1", \
      "start": 3056601, \
      "startMax": 0, \
      "end": 0, \
      "endMin": 0, \
      "endMax": 0, \
      "referenceBases": "C", \
      "alternateBases": "T", \
      "assemblyId": "GRCh38", \
      "includeDatasetResponses": "ALL"}'

Example Response:

.. code-block:: javascript

    {
    "beaconId": "localhost:5050",
    "apiVersion": "1.0.0",
    "exists": true,
    "error": null,
    "alleleRequest": {
        "referenceName": "1",
        "start": 3056601,
        "startMin": 0,
        "startMax": 0,
        "end": 0,
        "endMin": 0,
        "endMax": 0,
        "referenceBases": "C",
        "assemblyId": "GRCh38",
        "datasetIds": [],
        "includeDatasetResponses": "ALL",
        "alternateBases": "T"
    },
    "datasetAlleleResponses": [
        {
            "datasetId": "DATASET2",
            "externalUrl": "https://datasethost.org/dataset2",
            "note": "example dataset number 2",
            "variantCount": 63,
            "callCount": 5008,
            "sampleCount": 2504,
            "exists": true,
            "frequency": 0.0125799,
            "info": [
                {
                    "accessType": "PUBLIC"
                }
            ],
            "error": null
        },
        {
            "datasetId": "DATASET1",
            "externalUrl": "https://datasethost.org/dataset1",
            "note": "example dataset number 1",
            "variantCount": 0,
            "callCount": 0,
            "sampleCount": 0,
            "frequency": 0,
            "exists": false,
            "info": [
                {
                    "accessType": "PUBLIC"
                }
            ],
            "error": null
        }
    ]
    }

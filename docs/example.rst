Beacon API Examples
===================

The Beacon API consists of the following endpoints:

* ``/`` beacon information endpoint;
* ``/service-info`` GA4GH compliant information endpoint;
* ``/query`` - retrieving and filtering information from the beacon.

For the full specification consult: `Beacon API 1.0.0+ specification <https://github.com/ga4gh-beacon/specification>`_.

The Beacon API specification allows for additional properties, thus we add the following fields to
``/query`` endpoint to handle wildcard responses:

* ``referenceBases``
* ``alternateBases``
* ``variantType``

And variant location information to determine the region:

* ``start``
* ``end``

The requests are validated against a JSON schema, while for the responses we validate (via unit tests)
that they adhere to the required format.


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
        "id": "CSC",
        "name": "CSC - IT Center for Science",
        "description": "Finnish expertise in ICT for research, education, culture and public administration",
        "address": "Keilaranta 14, Espoo, finland",
        "welcomeUrl": "https://www.csc.fi/",
        "contactUrl": "https://www.csc.fi/contact-info",
        "logoUrl": "https://www.csc.fi/documents/10180/161914/CSC_2012_LOGO_RGB_72dpi.jpg",
        "info": {
          "orgInfo": "CSC represents Finland in the ELIXIR partner nodes"
        }
      },
      "description": "Beacon API Web Server based on the GA4GH Beacon API",
      "version": "1.0.0",
      "welcomeUrl": "https://ega-archive.org/",
      "alternativeUrl": "https://ega-archive.org/",
      "createDateTime": "2018-07-25T00:00:00Z",
      "updateDateTime": "2018-12-01T10:28:07Z",
      "datasets": [{
        "id": "urn:hg:1000genome",
        "name": "1000 genomoe",
        "externalUrl": "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/",
        "description": "Data from 1000 genome project",
        "assemblyId": "GRCh38",
        "variantCount": 84360986,
        "callCount": 79423363,
        "sampleCount": 2504,
        "version": "v0.4",
        "info": {
          "accessType": "PUBLIC"
        },
        "createDateTime": "2013-05-02T12:00:00Z",
        "updateDateTime": "2013-05-02T12:00:00Z"
      }],
      "sampleAlleleRequests": [{
        "alternateBases": "C",
        "referenceBases": "T",
        "referenceName": "MT",
        "start": 9,
        "assemblyId": "GRCh38",
        "includeDatasetResponses": "ALL"
      }, {
        "alternateBases": "A",
        "referenceBases": "G",
        "referenceName": "MT",
        "start": 7599,
        "assemblyId": "GRCh38",
        "datasetIds": ["urn:hg:exampleid-mt"],
        "includeDatasetResponses": "HIT"
      }, {
        "variantType": "SNP",
        "referenceBases": "G",
        "referenceName": "Y",
        "start": 7267243,
        "assemblyId": "GRCh38"
      }],
      "info": {
        "key": "value"
      }
    }

GA4GH Info Endpoint
-------------------------------------

.. code-block:: console

    $ curl -X GET 'http://localhost:5050/service-info'

Example Response:

.. code-block:: javascript

  {
    "id": "localhost:5050",
    "name": "GA4GHBeacon at CSC",
    "type": "org.ga4gh:beacon:1.1.0",
    "description": "Beacon API Web Server based on the GA4GH Beacon API",
    "organization": {
        "name": "CSC - IT Center for Science",
        "url": "https://www.csc.fi/"
    },
    "contactUrl": "https://www.csc.fi/contact-info",
    "documentationUrl": "https://beacon-network.readthedocs.io/en/latest/",
    "createdAt": "2019-09-04T12:00:00Z",
    "updatedAt": "2019-09-05T05:55:18Z",
    "environment": "prod",
    "version": "1.7.2"
  }

Query Endpoint
--------------

An example ``GET`` request and response to the ``query`` endpoint:

.. code-block:: console

    $ curl -X GET \
      'http://localhost:5050/query?referenceName=MT&referenceBases=A&start=14036&assemblyId=GRCh38&alternateBases=G'

Example Request:

.. code-block:: javascript

    {
      "beaconId": "localhost:5050",
      "apiVersion": "1.0.0",
      "exists": true,
      "alleleRequest": {
        "referenceName": "MT",
        "start": 14036,
        "referenceBases": "A",
        "assemblyId": "GRCh38",
        "datasetIds": [],
        "includeDatasetResponses": "NONE",
        "alternateBases": "G"
      },
      "datasetAlleleResponses": []
    }


An example ``POST`` request and response to the ``query`` endpoint:

.. code-block:: console

    $ curl -X POST \
      'http://localhost:5050/query' \
      -d '{"referenceName": "MT", \
      "start": 14036, \
      "referenceBases": "A", \
      "alternateBases": "G", \
      "assemblyId": "GRCh38", \
      "includeDatasetResponses": "HIT"}'

Example Response:

.. code-block:: javascript

    {
      "beaconId": "localhost:5050",
      "apiVersion": "1.0.0",
      "exists": true,
      "alleleRequest": {
        "referenceName": "MT",
        "start": 14036,
        "referenceBases": "A",
        "assemblyId": "GRCh38",
        "datasetIds": [],
        "includeDatasetResponses": "HIT",
        "alternateBases": "G"
      },
      "datasetAlleleResponses": [{
        "datasetId": "urn:hg:1000genome",
        "referenceName": "MT",
        "externalUrl": "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/",
        "note": "Data from 1000 genome project",
        "sampleCount": 2,
        "callCount": 2534,
        "exists": true,
        "referenceBases": "A",
        "alternateBases": "G",
        "start": 14036,
        "end": 14037,
        "variantType": "SNP",
        "frequency": 0.000789266,
        "variantCount": 1,
        "info": {
          "accessType": "PUBLIC"
        }
      }]
    }

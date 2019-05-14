Optional Features
=================

The Beacon specification contains some optional features that may be utilised or not.

.. _handover-protocol:

Handover Protocol
-----------------

The handover protocol is a feature comparable to `HATEOAS and HAL <https://restfulapi.net/hateoas/>`_. It can be used to convey
extra information regarding the Beacon service, or the dataset response.
More information about the handover protocol can be read from the `Beacon Project page <https://beacon-project.io/roadmap/handover.html>`_ and
Beacon Specification's `handover issue <https://github.com/ga4gh-beacon/specification/issues/114>`_ at Github.

The handover protocol can be configured in ``config.ini`` as follows:

.. literalinclude:: /../beacon_api/conf/config.ini
   :language: python
   :lines: 71-87

.. note:: Handover protocol is disabled by default, as shown by the commented out ``drs`` variable. This variable should point
          to the server, which serves the additional data. To enable the handover protocol, uncomment the ``drs`` variable.

The handover protocol will generate new objects to the ``beacon`` root object according to information given in the
``beacon_paths`` variable and to the ``includeDatasetResponses`` object according to information in ``dataset_paths``.
The line is spliced, so that the first CSV element becomes the ``label`` key in the handover, the second element becomes
the ``description`` key and the third element becomes the ``url`` key.

Taking the first line from ``dataset_paths`` as an example, produces an object in the ``includeDatasetResponses`` object as follows:

.. code-block:: javascript

    {
        "datasetHandover": [
            {
                "handoverType": {
                    "id": "CUSTOM",
                    "label": "Variants"
                },
                "description": "browse the variants matched by the query",
                "url": "https://examplebrowser.org/dataset/{dataset}/browser/variant/{chr}-{start}-{ref}-{alt}"
            }
        ]
    }

.. _mate-name:

MateName Fusions
----------------

This extension deals with processing ``SVTYPE=BND`` where each adjacency ties together
2 breakends. Refer to Page 20 of the `VCF documentation <https://samtools.github.io/hts-specs/VCFv4.3.pdf>`_
for more information.

+-------+----------+------------------------------------------------------------+
| REF   | ALT      | Meaning                                                    |
+-------+----------+------------------------------------------------------------+
| s     | ``t[p[`` | piece extending to the right of p is joined after t        |
+-------+----------+------------------------------------------------------------+
| s     | ``t]p]`` | reverse comp piece extending left of p is joined after t   |
+-------+----------+------------------------------------------------------------+
| s     | ``]p]t`` |  piece extending to the left of p is joined before t       |
+-------+----------+------------------------------------------------------------+
| s     | ``[p[t`` | reverse comp piece extending right of p is joined before t |
+-------+----------+------------------------------------------------------------+


.. note:: Where ``p`` is ``chr:pos``.

Example queries:

.. code-block:: console

    localhost:5050/query?referenceName=1&\
                        referenceBases=N&\
                        start=108796059&\
                        assemblyId=GRCh38&\
                        variantType=BND&\
                        end=121482216&\
                        datasetIds=urn:hg:1000genome&\
                        includeDatasetResponses=HIT

    localhost:5050/query?referenceName=1&\
                         referenceBases=N&\
                         start=108796059&\
                         assemblyId=GRCh38&\
                         mateName=10&\
                         end=121482216&\
                         datasetIds=urn:hg:1000genome&\
                         includeDatasetResponses=HIT

    localhost:5050/query?referenceName=1&\
                         referenceBases=N&\
                         startMin=108796058&\
                         startMax=108796059&\
                         assemblyId=GRCh38&\
                         mateName=10&\
                         endMin=121482215&\
                         endMax=121482216&\
                         datasetIds=urn:hg:1000genome&\
                         includeDatasetResponses=HIT


Currently querying for a ``BND`` using ``startMin``, ``startMax`` and ``endMin``, ``endMax``
with ``variantType=BND`` has the response illustrated below.
Fixed ``start`` and ``end`` can be utilised, as well as ``mateName`` as depicted above.

.. note:: By default when using ``mateName``, ``variantType`` is implicit ``BND``, 
          but it can also be set in an explicit manner using both ``mateName`` and
          ``variantType=BND`` in a query.

.. code-block:: javascript

    {
    "beaconId": "localhost:5050",
    "apiVersion": "1.1.0",
    "exists": true,
    "alleleRequest": {
        "referenceName": "1",
        "referenceBases": "N",
        "assemblyId": "GRCh38",
        "includeDatasetResponses": "HIT",
        "datasetIds": [
            "urn:hg:1000genome"
        ],
        "startMin": 108796058,
        "startMax": 108796059,
        "endMin": 121482215,
        "endMax": 121482216
    },
    "datasetAlleleResponses": [
        {
            "datasetId": "urn:hg:1000genome",
            "referenceName": "1",
            "mateName": "10",
            "referenceID": "137_1",
            "mateID": "137_2",
            "mateStart": 121482216,
            "externalUrl": "ftp://example",
            "note": "Data",
            "variantCount": 0,
            "callCount": 0,
            "sampleCount": 1,
            "frequency": 0,
            "exists": true,
            "referenceBases": "N",
            "alternateBases": "N[CHR10:121482216[",
            "variantType": "BND",
            "start": 108796058,
            "end": 108796059,
            "info": {
                "accessType": "PUBLIC"
            }
        },
        {
            "datasetId": "urn:hg:1000genome",
            "referenceName": "10",
            "mateName": "1",
            "referenceID": "137_2",
            "mateID": "137_1",
            "mateStart": 108796059,
            "externalUrl": "ftp://example",
            "note": "Data",
            "variantCount": 0,
            "callCount": 0,
            "sampleCount": 1,
            "frequency": 0,
            "exists": true,
            "referenceBases": "N",
            "alternateBases": "]CHR1:108796059]N",
            "variantType": "BND",
            "start": 121482215,
            "end": 121482216,
            "info": {
                "accessType": "PUBLIC"
            }
        }
    ]
    }


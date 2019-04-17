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
   :lines: 68-84

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

TBD


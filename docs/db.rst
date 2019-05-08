.. _database:

Database
========

We use a PostgreSQL database (version 9.6+) for working with beacon data.
For more information on setting up the database consult :ref:`database-setup`.

.. attention:: We recommend https://pgtune.leopard.in.ua/#/ for establishing PostgreSQL
             configuration parameters, in order to optimised database setup.

             e.g. for PostgreSQL running on 8GB of RAM setting ``shared_buffers = 2GB``
             ``effective_cache_size = 6GB`` can improve query performance.

.. hint:: Additional indexes can be added to improve query time performance

          .. code-block:: sql

              CREATE INDEX data_needed ON beacon_data_table
                USING btree(datasetId, chromosome, start, reference, alternate, varianttype,
                            frequency, "end");


We use the DB schema below as a means for providing making data accessible as described by
the Beacon API specification.

When designing the DB schema we also took into consideration information contained in ``*.vcf`` files.

Information for the metadata table currently needs to be provided by the data submitter,
as such information cannot be extracted from ``*.vcf`` files.

The Data Provider can use the ``beacon_init`` utility to load data, but if Data Provider has
a previous Database we recommend to skip the ``beacon_init`` utility and set up the database
using one of the solutions:

* creating a DB view that matches the DB schema for the beacon python server as described below;
* migrate the database to match the DB schema;
* keep own database, but modify the queries in :meth:`beacon_api.utils.data_query`.


.. literalinclude:: /../data/init.sql
   :language: sql
   :lines: 1-82

.. note:: In order to retrieve ``HIT`` and ``MISS`` as per to the API specification,
          we make use of the queries exemplified below.


For ``HIT`` results, example query below searches in all datasets:

.. code-block:: sql

    SELECT a.datasetId as "datasetId", b.accessType as "accessType", a.chromosome as "referenceName",
    a.reference as "referenceBases", a.alternate as "alternateBases", a.start as "start", a.end as "end",
    b.externalUrl as "externalUrl", b.description as "note",
    a.alleleCount as "variantCount", a.variantType as "variantType",
    a.callCount as "callCount", b.sampleCount as "sampleCount",
    a.frequency, "TRUE" as "exists"
    FROM beacon_data_table a, beacon_dataset_table b
    WHERE a.datasetId=b.datasetId
    AND b.assemblyId='GRCh38'
    AND (a.start=3056601
    AND NULL
    AND NULL AND NULL
    AND NULL AND NULL
    AND coalesce(a.reference LIKE any('T'), true)
    AND coalesce(a.variantType=NULL, true)
    AND coalesce(a.alternate LIKE any('C'), true))
    AND a.chromosome='Y'
    AND coalesce(b.accessType = any('REGISTERED', 'PUBLIC'), true)
    AND coalesce(a.datasetId = any('DATASET2'), true) ;

For ``MISS`` results, we would add:

.. code-block:: sql

    SELECT DISTINCT ON (datasetId)
    datasetId as "datasetId", accessType as "accessType",
    'Y' as "referenceName", "FALSE" as "exists"
    FROM beacon_dataset_table
    WHERE AND coalesce(b.accessType = any('REGISTERED', 'PUBLIC'), true)
    AND assemblyId='GRCh38'
    AND coalesce(a.datasetId = any('DATASET2'), true) ;

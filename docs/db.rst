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

Information for the metadata table, currently needs to be provided by the data submitter,
as such information cannot be extracted from ``*.vcf`` files.

The Data Provider can use the ``beacon_init`` utility to load data, but if Data Provider has
a previous Database we recommend to skip the ``beacon_init`` utility and set up the database
using one of the solutions:

* creating a DB view that matches the DB schema for the beacon python server as described below;
* migrate the database to match the DB schema;
* keep own database, but modify the queries in :meth:`beacon_api.utils.data_query`.


.. literalinclude:: /../data/init.sql
   :language: sql
   :lines: 1-62

.. note:: In order to retrieve bot HIT and MISS (according) to the API specification,
          we make use of the same query structure, exemplified below.


For ``HIT`` results, example query below searches in all datasets:

.. code-block:: sql

    SELECT  a.datasetId as "datasetId", b.accessType as "accessType",
            a.chromosome as "referenceName",
            b.externalUrl as "externalUrl", b.description as "note",
            a.alleleCount as "sampleCount", a.variantType as "variantType",
            a.callCount as "callCount",
            a.frequency, TRUE as "exists"
            FROM beacon_data_table a, beacon_dataset_table b
            WHERE a.datasetId=b.datasetId
            AND  (a.start=3056601 AND TRUE
            AND TRUE AND TRUE
            AND TRUE AND TRUE
            AND TRUE AND a.reference='T' AND TRUE  AND a.alternate='C')
            AND a.chromosome='Y'
            AND b.accessType IN ('REGISTERED', 'PUBLIC') AND TRUE ;

For ``MISS`` results, example query below searches in all ``DATASET2``:

.. code-block:: sql

    SELECT DISTINCT ON (a.dataset_id) a.datasetId as "datasetId", b.accessType as "accessType",
                        a.chromosome as "referenceName",
                        b.externalUrl as "externalUrl", b.description as "note",
                        a.alleleCount as "sampleCount", a.variantType as "variantType",
                        a.callCount as "callCount",
                        a.frequency, FALSE as "exists"
                        FROM beacon_data_table a, beacon_dataset_table b
                        WHERE a.datasetId=b.datasetId
                        AND NOT (a.start=3056601 AND TRUE
                        AND TRUE AND TRUE
                        AND TRUE AND TRUE
                        AND TRUE AND a.reference='T' AND TRUE AND a.alternate='C')
                        AND a.chromosome='Y'
                        AND b.accesstype IN ('REGISTERED', 'PUBLIC')
                        <> a.dataset_id IN ('DATASET2') ;

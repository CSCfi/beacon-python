.. _database:

Database
========

We use a PostgreSQL database (version 9.6+) for working beacon data.
For more information on setting up the database consult :ref:`database-setup`.

.. warning:: Database tables are subject to change as we tune the performance.

We use the DB schema below as a means for providing data contained in ``*.vcf`` file and making
it accessible via the Beacon API specification.

Information for the metadata table, currently needs to be provided by the data submitter,
as additional information, that cannot be extracted from ``*.vcf`` files, is required.

.. literalinclude:: /../data/init.sql
   :language: sql
   :lines: 1-57

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

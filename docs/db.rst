.. _database:

Database
========

We use a PostgreSQL database (version 9.6+) for working beacon data.
For more information on setting up the database consult :ref:`database-setup`.

We use the DB schema below as a means for providing data contained in ``*.vcf`` file and making
it accessible via the Beacon API specification.

Information for the metadata table, currently needs to be provided by the data submitter,
as additional information, that cannot be extracted from ``*.vcf`` files, is required.

.. literalinclude:: /../data/init.sql
   :language: sql
   :lines: 1-35

.. note:: In order to retrieve bot HIT and MISS (according) to the API specification,
          we make use of the same query structure, exemplified below.


For ``HIT`` results:

.. code-block:: sql

    SELECT DISTINCT ON (a.dataset_id) a.dataset_id as "datasetId", b.accessType as "accessType",
                                b.externalUrl as "externalUrl", b.description as "note",
                                a.variantcount as "variantCount",
                                a.callcount as "callCount", a.samplecount as "sampleCount",
                                a.frequency, TRUE as "exists"
                                FROM beacon_data_table a, beacon_dataset_table b
                                WHERE a.dataset_id=b.dataset_id
                                AND  (a.start=3056601 AND TRUE
                                AND TRUE AND TRUE
                                AND TRUE AND TRUE
                                AND TRUE AND a.reference='T' AND a.alternate='C')
                                AND b.accesstype IN ('REGISTERED', 'PUBLIC') AND TRUE ;

For ``MISS`` results:

.. code-block:: sql

    SELECT DISTINCT ON (a.dataset_id) a.dataset_id as "datasetId", b.accessType as "accessType",
                                b.externalUrl as "externalUrl", b.description as "note",
                                a.variantcount as "variantCount",
                                a.callcount as "callCount", a.samplecount as "sampleCount",
                                a.frequency, FALSE as "exists"
                                FROM beacon_data_table a, beacon_dataset_table b
                                WHERE a.dataset_id=b.dataset_id
                                AND NOT (a.start=3056601 AND TRUE
                                AND TRUE AND TRUE
                                AND TRUE AND TRUE
                                AND TRUE AND a.reference='T' AND a.alternate='C')
                                AND b.accesstype IN ('REGISTERED', 'PUBLIC')
                                <> a.dataset_id IN ('DATASET2') ;

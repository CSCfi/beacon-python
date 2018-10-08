Database schema
===============

.. note:: The Database and the queries are subject to change.

We use a PostgreSQL database (version 9.6+) for working beacon data.
For more information on seting up the database consult :ref:`database-setup`.

.. literalinclude:: /../data/init.sql
   :language: sql
   :lines: 1-31

Example queries to the database

.. code-block:: sql

    SELECT DISTINCT ON (a.dataset_id) a.dataset_id as "datasetId", b.accessType as "accessType",
                                b.externalUrl as "externalUrl", b.description as "note",
                                a.variantcount as "variantCount",
                                a.callcount as "callCount", a.samplecount as "sampleCount",
                                a.frequency, TRUE as "exists"
                                FROM beacon_data_table a, beacon_dataset_table b
                                WHERE a.dataset_id=b.dataset_id
                                AND  (a.start>=3056601 AND TRUE
                                AND TRUE AND TRUE
                                AND TRUE AND TRUE
                                AND TRUE AND a.alternate='T')
                                AND b.accesstype IN ('REGISTERED', 'PUBLIC') AND TRUE ;

.. code-block:: sql

    SELECT DISTINCT ON (a.dataset_id) a.dataset_id as "datasetId", b.accessType as "accessType",
                                b.externalUrl as "externalUrl", b.description as "note",
                                a.variantcount as "variantCount",
                                a.callcount as "callCount", a.samplecount as "sampleCount",
                                a.frequency, FALSE as "exists"
                                FROM beacon_data_table a, beacon_dataset_table b
                                WHERE a.dataset_id=b.dataset_id
                                AND NOT (a.start>=3056601 AND TRUE
                                AND TRUE AND TRUE
                                AND TRUE AND TRUE
                                AND TRUE AND a.alternate='T')
                                AND b.accesstype IN ('REGISTERED', 'PUBLIC')
                                <> a.dataset_id IN ('DATASET2') ;

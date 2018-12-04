Testing
=======

.. note:: Unit tests and integration tests are automatically executed with every PR to
          https://github.com/CSCfi/beacon-python

Unit Testing
------------

In order to run the unit tests and `flake8 <http://flake8.pycqa.org/en/latest/>`_ (coding style guide)
we are using `tox <http://tox.readthedocs.io/>`_:

.. code-block:: console

    $ tox


Integration Testing
-------------------

In order to run the integration tests, makes use of :ref:`s2i-build`:

.. code-block:: console

    $ git clone https://github.com/CSCfi/beacon-python
    $ cd beacon-python
    $ s2i build . centos/python-36-centos7 cscfi/beacon-python
    $ cd deploy
    $ docker-compose up -d
    $ docker-compose exec beacon beacon_init data/ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf.gz data/example_metadata.json
    $ docker-compose exec postgres psql -U beacon beacondb -c "INSERT INTO beacon_dataset_counts_table (datasetId, callCount, variantCount) VALUES ('urn:hg:1000genome', 1, 1)"
    $ python test/integ_test.py

The integration tests will build a docker image of the ``beacon-python`` and make use of
`docker compose <https://docs.docker.com/compose/>`_ to deploy the Web Server and an associated
PostgreSQL Database. Next step is to load mock data and last step is to run the integration tests.


Load Testing
------------

Load Testing scenarios

* Scenario 1 ``GET /info``
* Scenario 2 ``GET /query`` and ``POST /query`` (all, miss, hit)
* Scenario 3 ``GET /query`` and ``POST /query`` (all, miss, hit and (REGISTERED))
* Scenario 4 ``GET /query`` and ``POST /query`` that has multiple parameters for a more complex query (e.g. startMin, startMax and others) also test with (all, miss, hit) and (REGISTERED)

Example testing with `locust.io <http://locust.io/>`_

.. code-block:: python

    from locust import HttpLocust, TaskSet, task

    class APIBehavior(TaskSet):
    """Test Tasks for Beacon API."""

    @task
    def get_info(self):
        """Test the info endpoint.

        The only endpoint that has some sort of caching.
        """
        self.client.get("/")

    @task
    def get_query(self):
        """Test GET query endpoint."""
        self.client.get("/query?assemblyId=GRCh38&referenceName=MT&start=10&referenceBases=T&alternateBases=C&includeDatasetResponses=HIT")


    class APITest(HttpLocust):
    """Test Beacon API."""

    task_set = APIBehavior
    min_wait = 5000
    max_wait = 9000

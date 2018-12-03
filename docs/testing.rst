Testing
=======

.. note:: Unit tests and integration tests are automatically executed with every PR to
          https://github.com/CSCfi/beacon-python

Unit Testing
------------

In order to run the unit tests and flake8 we are using tox:

.. code-block:: console

    $ tox


Integration Testing
-------------------

In order to run the integration tests:

.. code-block:: console

    $ git clone https://github.com/CSCfi/beacon-python
    $ cd beacon-python
    $ s2i build . centos/python-36-centos7 cscfi/beacon-python
    $ cd deploy
    $ docker-compose up -d
    $ python test/integ_test.py


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

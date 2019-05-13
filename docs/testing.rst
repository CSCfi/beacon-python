Testing
=======

.. note:: Unit tests and integration tests are automatically executed with every PR to
          https://github.com/CSCfi/beacon-python

Unit Testing
------------

In order to run the unit tests, security checks with `bandit <https://github.com/PyCQA/bandit>`_,
Sphinx documentation check for links consistency and HTML output
and `flake8 <http://flake8.pycqa.org/en/latest/>`_ (coding style guide)
`tox <http://tox.readthedocs.io/>`_. To run the unit tests in parallel use:

.. code-block:: console

    $ tox -p auto

To run environments seprately use:

.. code-block:: console

    $ # list environments
    $ tox -l
    $ # run flake8
    $ tox -e flake8
    $ # run bandit
    $ tox -e bandit
    $ # run docs
    $ tox -e docs


Integration Testing
-------------------

In order to run the integration tests, makes use of :ref:`s2i-build`:

.. code-block:: console

    $ git clone https://github.com/CSCfi/beacon-python
    $ cd beacon-python
    $ # please make sure to commit any changes before building otherwise s2i will not integrate them in build
    $ s2i build . centos/python-36-centos7 cscfi/beacon-python
    $ cd deploy/test
    $ docker-compose up -d
    $ docker-compose exec beacon beacon_init data/ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf.gz data/example_metadata.json
    $ docker-compose exec beacon beacon_init data/ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf.gz /exdata/example_metadata_registered.json
    $ docker-compose exec beacon beacon_init data/ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf.gz /exdata/example_metadata_controlled.json
    $ docker-compose exec beacon beacon_init data/ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf.gz /exdata/example_metadata_controlled1.json
    $ python test/run_tests.py

The integration tests will build a docker image of the ``beacon-python`` and make use of
`docker compose <https://docs.docker.com/compose/>`_ to deploy the Web Server and an associated
PostgreSQL Database as well as a mock OAuth2 authentication server.
Next step is to load mock data, as illustrated by the
``docker-compose exec`` commands above, and last step is to run the integration tests.

The ``integ_test.py`` contains the actual tests while the ``run_tests`` discovers the tests and runs them.


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
        self.client.get("/query?assemblyId=GRCh38&referenceName=MT&start=9&referenceBases=T&alternateBases=C&includeDatasetResponses=HIT")


    class APITest(HttpLocust):
    """Test Beacon API."""

    task_set = APIBehavior
    min_wait = 5000
    max_wait = 9000

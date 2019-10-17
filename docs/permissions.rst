.. _permissions:

Handling Permissions
====================

As per Beacon specification there are three types of permissions:

* ``PUBLIC`` - data available for anyone;
* ``REGISTERED`` - data available for users registered on a service for special credentials
  e.g. ELIXIR bona_fide or researcher status. Requires a JWT Token;
* ``CONTROLLED`` - data available for users that have been granted access to a protected resource by a Data Access Committee (DAC).


Registered Data
---------------

For retrieving ``REGISTERED`` permissions the function below forwards the TOKEN to another server
that validates the information in the token is for a registered user/token and retrieves a JSON
message that contains data regarding the Bona Fide status. Custom servers can be set up to mimic this functionality.

.. literalinclude:: /../beacon_api/permissions/ga4gh.py
   :language: python
   :lines: 72-82

The function below then checks for the existence of the ``ga4gh.AcceptedTermsAndPolicies`` and ``ga4gh.ResearcherStatus`` keys,
which will indicate, that the user has agreed to follow ethical researcher practices, and has been recognised by another esteemed
researcher.

.. literalinclude:: /../beacon_api/permissions/ga4gh.py
   :language: python
   :lines: 103-128

.. note:: The ``ga4gh.AcceptedTermsAndPolicies`` and ``ga4gh.ResearcherStatus`` keys' values must be equal to those mandated by GA4GH.

Controlled Data
---------------

.. note:: See https://tools.ietf.org/html/rfc7519 for more information on claims and JWT.
          A short intro on the JSON Web Tokens available at: https://jwt.io/introduction/

In order to retrieve permissions for the ``CONTROLLED`` datasets via a JWT token, we added a
permissions module :meth:`beacon_api.permissions` that aims to act as a platform where
add-ons are placed for processing different styles of permissions claims.

The main reason for choosing such a method of handling dataset permissions, is that
there is no standard way for delivering access to datasets via JWT Tokens
and each AAI authority provides different claims with different structures.

By default we include :meth:`beacon_api.permissions.ga4gh` add-on that offers the means to retrieve
permissions following the `GA4GH format <https://docs.google.com/document/d/11Wg-uL75ypU5eNu2p_xh9gspmbGtmLzmdq5VfPHBirE>`_ via a token provided by ELIXIR AAI.

If a token contains ``ga4gh_userinfo_claims`` JWT claim with ``ga4gh.ControlledAccessGrants``, these are parsed
and retrieved as illustrated in:

.. literalinclude:: /../beacon_api/permissions/ga4gh.py
   :language: python
   :lines: 85-100

The permissions are then passed in :meth:`beacon_api.utils.validate` as illustrated below:

.. literalinclude:: /../beacon_api/utils/validate.py
   :language: python
   :dedent: 16
   :lines: 179-192

If there is no claim for GA4GH permissions as illustrated above, they will not be added to
``controlled_datasets``.

More datasets can be added to the ``controlled_datasets`` ``set()`` by updating:

.. code-block:: python

    controlled_datasets.update(custom_add_on())


where ``custom_add_on()`` is a function one could add in :meth:`beacon_api.permissions`.

An example of such a function is :meth:`beacon_api.permissions.ga4gh` and the specific JWT claim it should parse.

.. attention:: JWT is validated against an AAI OAuth2 signing authority with the public key.
               This public key can be provided  either a JWK server or the environment variable
               ``PUBLIC_KEY``. See also: :ref:`oauth2`.

Access Resolution
-----------------

.. role:: green
.. role:: orange
.. role:: red
.. role:: blue

In the tables below we illustrate how the beacon server handles access to datasets.
We have integrated tests for these use cases that can be found at:
`beacon-python Github deploy tests <https://github.com/CSCfi/beacon-python/blob/master/deploy/test/integ_test.py>`_.

.. admonition:: Table Legend

          * colours:

              * :green:`green` is for ``PUBLIC`` datasets;
              * :orange:`orange` is for ``REGISTERED`` datasets;
              * :red:`red` is for ``CONTROLLED`` datasets;
              * :blue:`blue` is for errors in retrieving datasets, currently done via HTTP error statuses;
          *  ``[]`` - all available datasets are requested;
          * if a cell is empty it means no datasets are requested;
          * ✓ - is used to represent that:

            * a JWT ``TOKEN`` is present in the request - used for retrieving ``CONTROLLED`` datasets from JWT claim;
            * a user's ``BONA FIDE`` status can be retrieved - used for ``REGISTERED`` datasets
            * if the ✓ is not present that means (depending on the column) there is no ``TOKEN``
              or ``BONA FIDE`` is not provided;
          * ``PERMISSIONS`` column reflects the dataset permissions found in the JWT ``TOKEN`` claim, if column
            is empty no datasets are in that specific claim.

Default cases (no dataset IDs specified)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most queries to the beacon do not specify datasets IDs meaning a request does not contain the ``datasetIds`` parameter.
For such cases we handle permissions as illustrated below.

+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
| Requested datasets                                            | DB: :green:`1, 2`, :orange:`3, 4`, :red:`5, 6`                                                                            |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
| :green:`PUBLIC`    | :orange:`REGISTERED` | :red:`CONTROLLED` | TOKEN                                            | PERMISSIONS | BONA FIDE | RESPONSE                                     |
+====================+======================+===================+==================================================+=============+===========+==============================================+
|     ``[]``         |    ``[]``            |       ``[]``      |                                                  |             |           | :green:`1, 2`                                |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
|     ``[]``         |    ``[]``            |       ``[]``      | ✓                                                |             |           | :green:`1, 2`                                |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
|     ``[]``         |    ``[]``            |       ``[]``      | ✓                                                |             | ✓         | :green:`1, 2`, :orange:`3, 4`                |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
|     ``[]``         |    ``[]``            |       ``[]``      | ✓                                                | :red:`5, 6` |           | :green:`1, 2`, :red:`5, 6`                   |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
|     ``[]``         |    ``[]``            |       ``[]``      | ✓                                                | :red:`5, 6` | ✓         | :green:`1, 2`, :orange:`3, 4`, :red:`5, 6`   |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+

Specific cases (dataset IDs specified)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For cases in which the dataset IDs are specified we handle permissions as in the table below.

+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
| Requested datasets                                            | DB: :green:`1, 2`, :orange:`3, 4`, :red:`5, 6`                                                                            |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
| :green:`PUBLIC`    | :orange:`REGISTERED` | :red:`CONTROLLED` | TOKEN                                            | PERMISSIONS | BONA FIDE | RESPONSE                                     |
+====================+======================+===================+==================================================+=============+===========+==============================================+
|                    |                      | :red:`5, 6`       | ✓                                                | :red:`5`    |           | :red:`5`                                     |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
| :green:`1`         |                      | :red:`5`          |                                                  |             |           | :green:`1`                                   |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
|                    | :orange:`4`          | :red:`7`          | ✓                                                |             | ✓         | :orange:`4`                                  |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
|                    | :orange:`3`          |                   |                                                  |             |           | :blue:`401 Unauthorized`                     |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
|                    |                      | :red:`5`          |                                                  |             |           | :blue:`401 Unauthorized`                     |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
|                    | :orange:`4`          |                   | ✓                                                |             |           | :blue:`403 Forbidden`                        |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
|                    |                      | :red:`6`          | ✓                                                | :red:`7`    |           | :blue:`403 Forbidden`                        |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+
| :green:`2`         |                      | :red:`6`          | ✓                                                | :red:`7`    |           | :green:`2`                                   |
+--------------------+----------------------+-------------------+--------------------------------------------------+-------------+-----------+----------------------------------------------+

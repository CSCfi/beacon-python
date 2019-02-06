.. _permissions:

Handling Permissions
====================

.. note:: See https://tools.ietf.org/html/rfc7519 for more information on claims and JWT

In order to retrieve permissions for ``CONTROLLED`` datasets via the JWT token, we add a
permissions module :meth:`beacon_api.permissions` that aims to provide an add-ons for
processing different styles of permissions claims. The main reason for choosing such a method
for handling ``CONTROLLED`` dataset permissions, as there is no standard for how to deliver
access to datasets via JWT and each AAI authority implements different claims.

We include by default :meth:`beacon_api.permissions.rems` that offers a means to retrieve
permissions from `REMS <https://rems2docs.rahtiapp.fi/>`_ via a token provided by ELIXIR AAI.

The token contains ``permissions_rems`` JWT claim with dataset permissions and these are retrieved
as illustrated in:

.. literalinclude:: /../beacon_api/permissions/rems.py
   :language: python
   :lines: 34-42

The permissions are then parsed in  :meth:`beacon_api.utils.validate` as illustrated below:

.. literalinclude:: /../beacon_api/utils/validate.py
   :language: python
   :dedent: 16
   :lines: 155-166

Other datasets can be added to the ``controlled_datasets`` set by updating that set
with custom written add-on (following the example of :meth:`beacon_api.permissions.rems`)
and the specific JWT claim.

.. attention:: JWT is validated against an AAI OAuth2 signing authority with the public key.
               This public key can be provided via a JWK server or the ``PUBLIC_KEY``.
               See also: :ref:`oauth2`.

Access Resolution
-----------------

.. role:: green
.. role:: orange
.. role:: red
.. role:: blue

In the tables below we illustrate how the beacon server handles access to datasets.
We have integrated tests for these use case that can be found at:
`beacon-python Github deploy tests <https://github.com/CSCfi/beacon-python/blob/master/deploy/test/integ_test.py>`_.

.. note:: Table Legend:

          *  ``[]`` - means all available datasets are requested;
          * if a cell is empty it means no datasets are requested;
          * ✓ - is used to represent that:

            * a ``TOKEN`` is present in the request - used for ``CONTROLLED`` datasets;
            * a user's ``BONA FIDE`` status can be retrieved - used for ``REGISTERED`` datasets.

Default cases (no dataset IDs specified)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most queries to the beacon do not specify datasets ids meaning a request does not contain the ``datasetIds`` parameter.
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

For case in which the dataset IDs are specified we handle permissions as in the table below.

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
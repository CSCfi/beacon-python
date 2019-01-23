.. _permissions:

Handling Permissions
====================

.. note:: See https://tools.ietf.org/html/rfc7519 for more information on claims and JWT

In order to retrieve permissions for ``CONTROLLED`` datasets via the JWT token, we add a
permissions module :meth:`beacon_api.permissions` that aims to provide an add-ons for
processing different styles of permissions claims.

We include by default :meth:`beacon_api.permissions.rems` that offers a means to retrieve
permissions from `REMS <https://rems2docs.rahtiapp.fi/>`_ via a token provided from ELIXIR AAI

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

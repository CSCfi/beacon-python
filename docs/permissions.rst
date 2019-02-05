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

.. attention:: JWT is validated against an AAI OAuth2 signing authority with the public key.
               This public key can be provided via a JWK server or the ``PUBLIC_KEY``.
               See also: :ref:`oauth2`.

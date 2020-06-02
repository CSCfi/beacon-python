--------------
Python Modules
--------------

.. automodule:: beacon_api
   :synopsis: The beacon_api package contains code for Beacon API.

.. autosummary::

    beacon_api.schemas
    beacon_api.api
    beacon_api.permissions
    beacon_api.utils
    beacon_api.conf
    beacon_api.extensions

***********
API Schemas
***********

.. automodule:: beacon_api.schemas

Example snippets from ``query.json``:

.. literalinclude:: /../beacon_api/schemas/query.json
   :language: javascript
   :lines: 11-15

.. literalinclude:: /../beacon_api/schemas/query.json
  :language: javascript
  :lines: 23-46

.. literalinclude:: /../beacon_api/schemas/query.json
   :language: javascript
   :lines: 78-108


**********
Beacon API
**********

.. automodule:: beacon_api.api

.. autosummary::
   :toctree: beacon_api.api

    beacon_api.api.info
    beacon_api.api.query
    beacon_api.api.exceptions

*****************
Utility Functions
*****************

.. automodule:: beacon_api.utils

.. autosummary::
   :toctree: beacon_api.utils

    beacon_api.utils.logging
    beacon_api.utils.db_load
    beacon_api.utils.validate_json
    beacon_api.utils.validate_jwt
    beacon_api.utils.data_query

******************
Permissions Addons
******************

.. automodule:: beacon_api.permissions

.. autosummary::
   :toctree: beacon_api.permissions

    beacon_api.permissions.ga4gh

*************
Configuration
*************

.. automodule:: beacon_api.conf

.. autosummary::
   :toctree: beacon_api.conf

   beacon_api.conf.config

**********
Extensions
**********

.. automodule:: beacon_api.extensions

.. autosummary::
   :toctree: beacon_api.extensions

    beacon_api.extensions.handover
    beacon_api.extensions.mate_name


:ref:`genindex` | :ref:`modindex`

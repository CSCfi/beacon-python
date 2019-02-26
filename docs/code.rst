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
  :lines: 41-56

.. literalinclude:: /../beacon_api/schemas/query.json
   :language: javascript
   :lines: 72-97


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
    beacon_api.utils.validate
    beacon_api.utils.data_query

******************
Permissions Addons
******************

.. automodule:: beacon_api.permissions

.. autosummary::
   :toctree: beacon_api.permissions

    beacon_api.permissions.rems

*************
Configuration
*************

.. automodule:: beacon_api.conf

.. autosummary::
   :toctree: beacon_api.conf

   beacon_api.conf.config


:ref:`genindex` | :ref:`modindex`

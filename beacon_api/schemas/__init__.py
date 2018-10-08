"""Load JSON Schemas.

The schemas represent a good way of checking the endpoint requests/responses that
it adheres to the API specification.
Schemas available:

* ``query.json`` - for the ``/query`` endpoint request.
"""

import os
import json


def load_schema(name):
    """Load JSON schemas."""
    module_path = os.path.dirname(__file__)
    path = os.path.join(module_path, '{0}.json'.format(name))

    with open(os.path.abspath(path), 'r') as fp:
        data = fp.read()

    return json.loads(data)

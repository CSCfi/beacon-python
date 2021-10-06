"""Load JSON Schemas.

The JSON schemas represent a good method of checking that an endpoint's
requests/responses adhere to the API specification.
Schemas available:

* ``info.json`` - for the ``/info`` endpoint response;
* ``query.json`` - for the ``/query`` endpoint request;
* ``response.json`` - beacon API JSON response.
"""

import ujson
from typing import Dict
from pathlib import Path


def load_schema(name: str) -> Dict:
    """Load JSON schemas."""
    module_path = Path(__file__).resolve().parent
    path = module_path.joinpath(f"{name}.json")

    with open(str(path), "r") as fp:
        data = fp.read()

    return ujson.loads(data)

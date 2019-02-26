"""Parse permissions from ELIXIR token for REMS claim.

Current implementation is based on https://app.swaggerhub.com/apis-docs/ELIXIR-Finland/Permissions/1.2
where they JWT claim for permissions is ``permissions_rems`` and the permissions have the following format:

.. code-block:: javascript

    [
        {
          "affiliation": "",
          "datasets": [
            "EGAD01",
            "urn:hg:example-controlled"
          ],
          "source_signature": "",
          "url_prefix": ""
        },
        {
          "affiliation": "",
          "datasets": [
            "urn:hg:example-controlled",
            "EGAD02",
            "urn:hg:example-controlled3"
          ],
          "source_signature": "",
          "url_prefix": ""
        }
    ]

"""
from ..utils.logging import LOG


def get_rems_controlled(permissions_claim):
    """Retrieve datasets from REMS permissions JWT claim."""
    # We only want to get datasets once, thus the set which prevents duplicates
    LOG.info("Parsing REMS permissions.")
    datasets = set()
    for permission in permissions_claim:
        datasets.update(permission["datasets"])

    return datasets

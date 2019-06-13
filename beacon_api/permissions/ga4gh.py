"""Parse permissions from ELIXIR token for GA4GH claim.

Current implementation is based on https://github.com/CSCfi/elixir-rems-proxy/blob/2.0/permissions-api.yml

The JWT contains GA4GH DURI claims in the following form:

.. code-block:: javascript

    {
        "ga4gh.userinfo_claims": [
            "AffiliationAndRole",
            "ControlledAccessGrants",
            "AcceptedTermsAndPolicies",
            "ResearcherStatus"
        ]
    }

The actual dataset permissions are then requested from /userinfo endpoint, and take the form of:

.. code-block:: javascript

    {
        "ga4ghSignature": "c01b39c7a35ccc3b081a3e83d2c71fa9a767ebfeb45c69f08e17dfe3ef375a7b",
        "ga4gh": {
            "ControlledAccessGrants": [
                {
                    "value": "https://www.ebi.ac.uk/ega/EGAD000000000001",
                    "source": "https://ega-archive.org/dacs/EGAC00000000001",
                    "by": "dac",
                    "authoriser": "john.doe@dac.org",
                    "asserted": 1546300800,
                    "expires": 1577836800
                }
            ]
        }
    }

"""
import aiohttp

from ..api.exceptions import BeaconServerError
from ..utils.logging import LOG
from ..conf import OAUTH2_CONFIG


async def retrieve_dataset_permissions(token):
    """Retrieve GA4GH dataset permissions."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(OAUTH2_CONFIG.bona_fide) as r:
                json_body = await r.json()
                LOG.info('Retrieve GA4GH dataset permissions.')
                return json_body.get("ga4gh", None)
    except Exception:
        raise BeaconServerError("Could not retrieve GA4GH dataset permissions.")


async def get_ga4gh_controlled(token, token_claim):
    """Retrieve datasets from GA4GH permissions JWT claim."""
    # We only want to get datasets once, thus the set which prevents duplicates
    LOG.info("Parsing GA4GH permissions.")
    datasets = set()
    # Check if the token contains a claim for GA4GH permissions
    if 'ga4gh.ControlledAccessGrants' in token_claim:
        # Contact /userinfo with token to get GA4GH permissions
        ga4gh = await retrieve_dataset_permissions(token)
        # If the /userinfo endpoint responded with permissions, retrieve and parse them
        if 'ControlledAccessGrants' in ga4gh:
            # Extract dataset key and split by `/` to remove potential URL prefix
            # the dataset id in the resulting list will always be the last element
            datasets.update([p["value"].split('/')[-1] for p in ga4gh["ControlledAccessGrants"]])

    return datasets

"""Parse permissions and statuses from ELIXIR token for GA4GH claim.

Current implementation is based on https://docs.google.com/document/d/11Wg-uL75ypU5eNu2p_xh9gspmbGtmLzmdq5VfPHBirE

The JWT contains GA4GH DURI claims in the following form:

.. code-block:: javascript

    {
        "ga4gh.userinfo_claims": [
            "ga4gh.AffiliationAndRole",
            "ga4gh.ControlledAccessGrants",
            "ga4gh.AcceptedTermsAndPolicies",
            "ga4gh.ResearcherStatus"
        ]
    }

The actual dataset permissions are then requested from /userinfo endpoint, and take the form of:

.. code-block:: javascript

    {
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

The statuses are also requested from /userinfo endpoint, and take the form of:

.. code-block:: javascript

    {
        "ga4gh": {
            "AcceptedTermsAndPolicies": [
                {
                    "value": "https://doi.org/10.1038/s41431-018-0219-y",
                    "source": "https://ga4gh.org/duri/no_org",
                    "by": "self",
                    "asserted": 1539069213,
                    "expires": 4694742813
                }
            ],
            "ResearcherStatus": [
                {
                    "value": "https://doi.org/10.1038/s41431-018-0219-y",
                    "source": "https://ga4gh.org/duri/no_org",
                    "by": "peer",
                    "asserted": 1539017776,
                    "expires": 1593165413
                }
            ]
        }
    }

"""
import aiohttp

from ..api.exceptions import BeaconServerError
from ..utils.logging import LOG
from ..conf import OAUTH2_CONFIG


async def retrieve_user_data(token):
    """Retrieve GA4GH user data."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(OAUTH2_CONFIG.userinfo) as r:
                json_body = await r.json()
                LOG.info('Retrieve GA4GH user data from ELIXIR AAI.')
                return json_body.get("ga4gh", None)
    except Exception:
        raise BeaconServerError("Could not retrieve GA4GH user data from ELIXIR AAI.")


async def get_ga4gh_controlled(token, token_claim):
    """Retrieve datasets from GA4GH permissions JWT claim."""
    # We only want to get datasets once, thus the set which prevents duplicates
    LOG.info("Parsing GA4GH dataset permissions claims.")
    datasets = set()
    # Check if the token contains a claim for GA4GH permissions
    if 'ga4gh.ControlledAccessGrants' in token_claim:
        # Contact /userinfo with token to get GA4GH permissions
        ga4gh = await retrieve_user_data(token)
        # If the /userinfo endpoint responded with user data, retrieve permissions and parse them
        if 'ControlledAccessGrants' in ga4gh:
            # Extract dataset key and split by `/` to remove potential URL prefix
            # the dataset id in the resulting list will always be the last element
            datasets.update([p["value"].split('/')[-1] for p in ga4gh["ControlledAccessGrants"] if "value" in p])

    return datasets


async def get_ga4gh_bona_fide(token, token_claim):
    """Retrieve Bona Fide status from GA4GH JWT claim."""
    LOG.info("Parsing GA4GH bona fide claims.")

    # User must have agreed to terms, and been recognized by a peer to be granted Bona Fide status
    terms = False
    status = False

    # Check if the token contains claims for GA4GH Bona Fide
    if 'ga4gh.AcceptedTermsAndPolicies' in token_claim and 'ga4gh.ResearcherStatus' in token_claim:
        # Contact /userinfo with token to get confirmation of Bona Fide status
        ga4gh = await retrieve_user_data(token)
        # If the /userinfo endpoint responded with user data, retrieve statuses and agreements and parse them
        if 'AcceptedTermsAndPolicies' in ga4gh:
            for accepted_terms in ga4gh["AcceptedTermsAndPolicies"]:
                if accepted_terms.get("value") == OAUTH2_CONFIG.bona_fide_value:
                    terms = True
        if 'ResearcherStatus' in ga4gh:
            for researcher_status in ga4gh["ResearcherStatus"]:
                if researcher_status.get("value") == OAUTH2_CONFIG.bona_fide_value:
                    status = True
        if terms and status:
            # User has agreed to terms and has been recognized by a peer, return True for Bona Fide status
            return True

    return False

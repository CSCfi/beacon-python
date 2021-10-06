"""Parse permissions and statuses from ELIXIR token for GA4GH claim.

Current implementation is based on https://github.com/ga4gh/data-security/blob/master/AAI/AAIConnectProfile.md

The ELIXIR AAI JWT payload contains a GA4GH Passport claim in the scope:

.. code-block:: javascript

    {
        "scope": "openid ga4gh_passport_v1",
        ...
    }

The token is then intended to be delivered to the /userinfo endpoint at ELIXIR AAI, which will respond with a list of
assorted third party JWTs that need to be sifted through to find the relevant tokens. Initially it can not be determined
which tokens contain the desired information.

.. code-block:: javascript

    {
        "ga4gh_passport_v1": [
            "JWT",
            "JWT",
            "JWT",
            ...
        ]
    }

Each third party token (JWT, RFC 7519) consists of three parts separated by dots, in the following manner: `header.payload.signature`.
This module processes the assorted tokens to extract the information they carry and to validate that data.

The process is carried out as such:
1. Take token (JWT)
2. Decode token
3a. Extract `type` key from the payload portion and check if the token type is of interest
3b. If the token is of the desired type, add it to list and continue, if not, discard this token and move to the next one
4. Extract `jku` key from the header portion (value is a URL that returns a JWK public key set)
5. Decode the complete token with the received public key
6. Validate the token claims
7. Extract the sought-after value from the `ga4gh_visa_v1` object's `value` key

Dataset permissions are read from GA4GH RI claims of the type "ControlledAccessGrants"

.. code-block:: javascript

    {
        "ga4gh_visa_v1": {
            "type": "ControlledAccessGrants",
            "value": "https://www.ebi.ac.uk/ega/EGAD000000000001",
            "source": "https://ega-archive.org/dacs/EGAC00000000001",
            "by": "dac",
            "asserted": 1546300800,
            "expires": 1577836800
        }
    }

Bona Fide status is read from GA4GH RI claims of the type "AcceptedTermsAndPolicies" and "ResearcherStatus", each being in their respective tokens.

.. code-block:: javascript

    {
        "ga4gh_visa_v1": {
            "type": "AcceptedTermsAndPolicies",
            "value": "https://doi.org/10.1038/s41431-018-0219-y",
            "source": "https://ga4gh.org/duri/no_org",
            "by": "self",
            "asserted": 1539069213,
            "expires": 4694742813
        }
    }

    {
        "ga4gh_visa_v1": {
            "type": "ResearcherStatus",
            "value": "https://doi.org/10.1038/s41431-018-0219-y",
            "source": "https://ga4gh.org/duri/no_org",
            "by": "peer",
            "asserted": 1539017776,
            "expires": 1593165413
        }
    }

"""
import base64
import ujson
from typing import Dict, List, Tuple

import aiohttp

from authlib.jose import jwt
from authlib.jose import JWTClaims
from typing import Optional

from ..api.exceptions import BeaconServerError
from ..utils.logging import LOG
from ..conf import OAUTH2_CONFIG


async def check_ga4gh_token(decoded_data: JWTClaims, token: str, bona_fide_status: bool, dataset_permissions: set) -> Tuple[set, bool]:
    """Check the token for GA4GH claims."""
    LOG.debug("Checking GA4GH claims from scope.")

    if "scope" in decoded_data:
        ga4gh_scopes = ["openid", "ga4gh_passport_v1"]
        token_scopes = decoded_data.get("scope").split(" ")

        if all(scope in token_scopes for scope in ga4gh_scopes):
            dataset_permissions, bona_fide_status = await get_ga4gh_permissions(token)

    return dataset_permissions, bona_fide_status


async def decode_passport(encoded_passport: str) -> List[Dict]:
    """Return decoded header and payload from encoded passport JWT.

    Public-key-less decoding inspired by the PyJWT library https://github.com/jpadilla/pyjwt
    """
    LOG.debug("Decoding GA4GH passport.")

    # Convert the token string into bytes for processing, and split it into segments
    decoded_passport = encoded_passport.encode("utf-8")  # `header.payload.signature`
    data, _ = decoded_passport.rsplit(b".", 1)  # data contains header and payload segments, the ignored segment is the signature segment
    segments = data.split(b".", 1)  # [header, payload]

    # Intermediary container
    verified_segments = []
    # Handle different implementations of public exponent
    # 65537 is recommended, but some use 65536 instead
    # pad the missing bytes, if needed
    for segment in segments:
        rem = len(segment) % 4
        if rem > 0:
            segment += b"=" * (4 - rem)
        verified_segments.append(segment)

    # Decode the verified token segments
    decoded_segments = [base64.urlsafe_b64decode(seg) for seg in verified_segments]

    # Convert the decoded segment bytes into dicts for easy access
    decoded_data = [ujson.loads(seg.decode("utf-8")) for seg in decoded_segments]

    return decoded_data


async def get_ga4gh_permissions(token: str) -> Tuple[set, bool]:
    """Retrieve GA4GH passports (JWTs) from ELIXIR AAI and process them into tangible permissions."""
    LOG.info("Handling permissions.")

    # Return variables
    dataset_permissions = set()
    bona_fide_status = False

    # Intermediary containers
    dataset_passports = []  # [(token, header)]
    bona_fide_passports = []  # [(token, header, payload)]

    # Get encoded passports (assorted JWTs) from /userinfo
    encoded_passports = await retrieve_user_data(token)

    # Pre-process the assorted passports (JWTs) for dataset permissions and bona fide status parsing
    if encoded_passports:
        # Decode the passports and check their type
        for encoded_passport in encoded_passports:
            # Decode passport
            header, payload = await decode_passport(encoded_passport)
            # Sort passports that carry dataset permissions
            pass_type = payload.get("ga4gh_visa_v1", {}).get("type")
            if pass_type == "ControlledAccessGrants":  # nosec
                dataset_passports.append((encoded_passport, header))
            # Sort passports that MAY carry bona fide status information
            if pass_type in ["AcceptedTermsAndPolicies", "ResearcherStatus"]:
                bona_fide_passports.append((encoded_passport, header, payload))

    # Parse dataset passports to extract dataset permissions and validate them
    dataset_permissions = await get_ga4gh_controlled(dataset_passports)
    # Parse bona fide passports to extract bona fide status and validate them
    bona_fide_status = await get_ga4gh_bona_fide(bona_fide_passports)

    return dataset_permissions, bona_fide_status


async def retrieve_user_data(token: str) -> Optional[str]:
    """Retrieve GA4GH user data."""
    LOG.debug("Contacting ELIXIR AAI /userinfo.")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(OAUTH2_CONFIG.userinfo) as r:
                json_body = await r.json()
                LOG.info("Retrieve GA4GH user data from ELIXIR AAI.")
                return json_body.get("ga4gh_passport_v1", None)
    except Exception:
        raise BeaconServerError("Could not retrieve GA4GH user data from ELIXIR AAI.")


async def get_jwk(url: str) -> Optional[Dict]:
    """Get JWK set keys to validate JWT."""
    LOG.debug("Retrieving JWK.")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                # This can be a single key or a list of JWK
                return await r.json()
    except Exception:
        # This is not a fatal error, it just means that we are unable to validate the permissions,
        # but the process should continue even if the validation of one token fails
        LOG.error(f"Could not retrieve JWK from {url}")
        return None


async def validate_passport(passport: Dict) -> JWTClaims:
    """Decode a passport and validate its contents."""
    LOG.debug("Validating passport.")

    # Passports from `get_ga4gh_controlled()` will be of form
    # passport[0] -> encoded passport (JWT)
    # passport[1] -> unverified decoded header (contains `jku`)
    # Passports from `get_bona_fide_status()` will be of form
    # passport[0] -> encoded passport (JWT)
    # passport[1] -> unverified decoded header (contains `jku`)
    # passport[2] -> unverified decoded payload

    # JWT decoding and validation settings
    # The `aud` claim will be ignored, because Beacon has no prior knowledge
    # as to where the token has originated from, and is therefore unable to
    # verify the intended audience. Other claims will be validated as per usual.
    claims_options = {"aud": {"essential": False}}

    # Attempt to decode the token and validate its contents
    # None of the exceptions are fatal, and will not raise an exception
    # Because even if the validation of one passport fails, the query
    # Should still continue in case other passports are valid
    try:
        # Get JWK for this passport from a third party provider
        # The JWK will be requested from a URL that is given in the `jku` claim in the header
        passport_key = await get_jwk(passport[1].get("jku"))
        # Decode the JWT using public key
        decoded_passport = jwt.decode(passport[0], passport_key, claims_options=claims_options)
        # Validate the JWT signature
        decoded_passport.validate()
        # Return decoded and validated payload contents
        return decoded_passport
    except Exception as e:
        LOG.error(f"Something went wrong when processing JWT tokens: {e}")


async def get_ga4gh_controlled(passports: List) -> set:
    """Retrieve dataset permissions from GA4GH passport visas."""
    # We only want to get datasets once, thus the set which prevents duplicates
    LOG.info("Parsing GA4GH dataset permissions.")
    datasets = set()

    for passport in passports:
        # Decode passport and validate its contents
        validated_passport = await validate_passport(passport)
        # Extract dataset id from validated passport
        # The dataset value will be of form `https://institution.org/urn:dataset:1000`
        # the extracted dataset will always be the last list element when split with `/`
        dataset = validated_passport.get("ga4gh_visa_v1", {}).get("value").split("/")[-1]
        # Add dataset to set
        datasets.add(dataset)

    return datasets


async def get_ga4gh_bona_fide(passports: List) -> bool:
    """Retrieve Bona Fide status from GA4GH JWT claim."""
    LOG.info("Parsing GA4GH bona fide claims.")

    # User must have agreed to terms, and been recognized by a peer to be granted Bona Fide status
    terms = False
    status = False

    for passport in passports:
        # Check for the `type` of visa to determine if to look for `terms` or `status`
        #
        # CHECK FOR TERMS
        passport_type = passport[2].get("ga4gh_visa_v1", {}).get("type")
        passport_value = passport[2].get("ga4gh_visa_v1", {}).get("value")
        if passport_type in "AcceptedTermsAndPolicies" and passport_value == OAUTH2_CONFIG.bona_fide_value:
            # This passport has the correct type and value, next step is to validate it
            #
            # Decode passport and validate its contents
            # If the validation passes, terms will be set to True
            # If the validation fails, an exception will be raised
            # (and ignored since it's not fatal), and terms will remain False
            await validate_passport(passport)
            # The token is validated, therefore the terms are accepted
            terms = True
        #
        # CHECK FOR STATUS
        if passport_value == OAUTH2_CONFIG.bona_fide_value and passport_type == "ResearcherStatus":
            # Check if the visa contains a bona fide value
            # This passport has the correct type and value, next step is to validate it
            #
            # Decode passport and validate its contents
            # If the validation passes, status will be set to True
            # If the validation fails, an exception will be raised
            # (and ignored since it's not fatal), and status will remain False
            await validate_passport(passport)
            # The token is validated, therefore the status is accepted
            status = True

        # User has agreed to terms and has been recognized by a peer, return True for Bona Fide status
    return terms and status

"""Info Endpoint.

Querying the info endpoint reveals information about existing datasets in this beacon
and their associated metadata.

.. note:: See ``beacon_api`` root folder ``__init__.py`` for changing values used here.
"""

from .. import __apiVersion__, __title__, __version__, __description__, __url__, __alturl__, __handover_beacon__
from .. import __createtime__, __updatetime__, __org_id__, __org_name__, __org_description__
from .. import __org_address__, __org_logoUrl__, __org_welcomeUrl__, __org_info__, __org_contactUrl__
from .. import __sample_queries__, __handover_drs__, __docs_url__
from ..utils.data_query import fetch_dataset_metadata
from ..extensions.handover import make_handover
from aiocache import cached
from aiocache.serializers import JsonSerializer


@cached(ttl=60, key="ga4gh_info", serializer=JsonSerializer())
async def ga4gh_info(host):
    """Construct the `Beacon` app information dict in GA4GH Discovery format.

    :return beacon_info: A dict that contain information about the ``Beacon`` endpoint.
    """
    beacon_info = {
        # TO DO implement some fallback mechanism for ID
        'id': '.'.join(reversed(host.split('.'))),
        'name': __title__,
        'description': __description__,
        'documentationUrl': __docs_url__,
        'contactUrl': __org_contactUrl__,
        'version': __version__
    }
    return beacon_info


@cached(ttl=60, key="info_key", serializer=JsonSerializer())
async def beacon_info(host, pool):
    """Construct the `Beacon` app information dict.

    :return beacon_info: A dict that contain information about the ``Beacon`` endpoint.
    """
    beacon_dataset = await fetch_dataset_metadata(pool)

    # If one sets up a beacon it is recommended to adjust these sample requests
    # for instance by adding a list of other samples in beacon_api/conf/sample_queries.json
    sample_allele_request = [{
        "alternateBases": "G",
        "referenceBases": "A",
        "referenceName": "MT",
        "start": 14036,
        "assemblyId": "GRCh38",
        "includeDatasetResponses": "ALL"
    }, {
        "variantType": "DUP",
        "referenceBases": "C",
        "referenceName": "19",
        "start": 36909436,
        "assemblyId": "GRCh38",
        "datasetIds": [
            "urn:hg:1000genome"
        ],
        "includeDatasetResponses": "HIT"},
        {
        "variantType": "INS",
        "referenceBases": "C",
        "referenceName": "1",
        "start": 104431389,
        "assemblyId": "GRCh38"
    }
    ]

    organization = {
        'id': __org_id__,
        'name': __org_name__,
        'description': __org_description__,
        'address': __org_address__,
        'welcomeUrl': __org_welcomeUrl__,
        'contactUrl': __org_contactUrl__,
        'logoUrl': __org_logoUrl__,
        'info': __org_info__,
    }

    beacon_info = {
        # TO DO implement some fallback mechanism for ID
        'id': '.'.join(reversed(host.split('.'))),
        'name': __title__,
        'apiVersion': __apiVersion__,
        'organization': organization,
        'description': __description__,
        'version': __version__,
        'welcomeUrl': __url__,
        'alternativeUrl': __alturl__,
        'createDateTime': __createtime__,
        'updateDateTime': __updatetime__,
        'datasets': beacon_dataset,
        'sampleAlleleRequests': __sample_queries__ or sample_allele_request,
        'info': {"achievement": "World's first 1.0 Beacon"},
    }

    if __handover_drs__:
        beacon_info['beaconHandover'] = make_handover(__handover_beacon__, [x['id'] for x in beacon_dataset])
    return beacon_info

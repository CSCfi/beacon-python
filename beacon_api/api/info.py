"""Info Endpoint.

Querying the info endpoint reveals information about existing datasets in this beacon
and their associated metadata.

.. note:: In this file is where one would change information about their beacon.
"""

from .. import __apiVersion__, __title__, __version__, __description__, __url__, __alturl__
from .. import __createtime__, __updatetime__, __org_id__, __org_name__, __org_description__
from .. import __org_address__, __org_logoUrl__, __org_welcomeUrl__, __org_info__, __org_contactUrl__
from ..utils.data_query import fetch_dataset_metadata


async def beacon_info(host, pool):
    """Construct the `Beacon` app information dict.

    :return beacon_info: A dict that contain information about the ``Beacon`` endpoint.
    """
    beacon_dataset = await fetch_dataset_metadata(pool)

    # TO DO provide more meaninful example specific to the endpoint data
    sample_allele_request = [{
        "alternateBases": "A",
        "referenceBases": "C",
        "referenceName": "17",
        "start": 6689,
        "assemblyId": "GRCh37",
        "datasetIds": None,
        "includeDatasetResponses": "NONE"
    }, {
        "alternateBases": "G",
        "referenceBases": "A",
        "referenceName": "1",
        "start": 14929,
        "assemblyId": "GRCh37",
        "datasetIds": [
            "DATASET1"
        ],
        "includeDatasetResponses": "ALL"},
        {
        "alternateBases": "CCCCT",
        "referenceBases": "C",
        "referenceName": "1",
        "start": 866510,
        "assemblyId": "GRCh37",
        "datasetIds": [
            "DATASET2",
            "DATASET3"
        ],
        "includeDatasetResponses": "HIT"
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
        # TO DO implement some faillback mechanism for ID
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
        'dataset': beacon_dataset,
        'sampleAlleleRequests': sample_allele_request,
        'info': [{"key": "value"}]
    }

    return beacon_info

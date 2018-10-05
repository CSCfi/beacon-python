from .. import __apiVersion__, __title__, __version__
from ..utils.data_query import fetch_dataset_metadata


async def beacon_info(host, pool):
    """
    Construct the `Beacon` dict that the info end point will return.

    :type Beacon: Dict
    :return Beacon: A dict that contain all the information about the `Beacon`.
    """
    beacon_dataset = await fetch_dataset_metadata(pool)

    beacon_allele_request = [{
        "alternateBases": "A",
        "referenceBases": "C",
        "referenceName": "17",
        "start": 6689,
        "assemblyId": "GRCh37",
        "datasetIds": None,
        "includeDatasetResponses": False
    }, {
        "alternateBases": "G",
        "referenceBases": "A",
        "referenceName": "1",
        "start": 14929,
        "assemblyId": "GRCh37",
        "datasetIds": [
            "EGAD00000000028"
        ],
        "includeDatasetResponses": "ALL"},
        {
        "alternateBases": "CCCCT",
        "referenceBases": "C",
        "referenceName": "1",
        "start": 866510,
        "assemblyId": "GRCh37",
        "datasetIds": [
            "EGAD00001000740",
            "EGAD00001000741"
        ],
        "includeDatasetResponses": "HIT"
    }
    ]

    organization = {
        'id': 'EGA',
        'name': 'European Genome-Phenome Archive (EGA)',
        'description': 'The European Genome-phenome Archive (EGA) is a service for permanent archiving and sharing of all types of personally identifiable \
        genetic and phenotypic data resulting from biomedical research projects.',
        'address': '',
        'welcomeUrl': 'https://ega-archive.org/',
        'contactUrl': 'mailto:beacon.ega@crg.eu',
        'logoUrl': 'https://ega-archive.org/images/logo.png',
        'info': None,
    }

    beacon_info = {
        # TO DO implement some faillback mechanism for ID
        'id': '.'.join(reversed(host.split('.'))),
        'name': __title__,
        'apiVersion': __apiVersion__,
        'organization': organization,
        'description': 'This <a href=\"http://ga4gh.org/#/beacon\">Beacon</a> is based on the GA4GH Beacon\
         <a href=\"https://github.com/ga4gh/beacon-team/blob/develop/src/main/resources/avro/beacon.avdl\">API 0.4</a>',
        'version': __version__,
        'welcomeUrl': 'https://ega-archive.org/beacon_web/',
        'alternativeUrl': 'https://ega-archive.org/beacon_web/',
        # TO DO - figure out how to dynamically get these dates
        'createDateTime': '2018-07-25T00:00.000Z',
        'updateDateTime': None,
        'dataset': beacon_dataset,
        'sampleAlleleRequests': beacon_allele_request,
        'info': [{"key": "string",
                  "value": "string"}]
    }

    return beacon_info
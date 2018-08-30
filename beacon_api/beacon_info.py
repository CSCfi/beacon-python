import models


def constructor():
    """
    The `constructor()` function constructs the `Beacon` dict that the info end point will return.

    :type Beacon: Dict
    :return Beacon: A dict that contain all the information about the `Beacon`.
    """
    # Here are some example requests.
    BeaconAlleleRequest = [{
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

    BeaconDataset = []
    dbObject = models.Beacon_dataset_table
    # List of all the rows in the beacon_dataset_table
    dbTable = dbObject.query.all()

    for row in dbTable:
        asd = {
            "id": row.id,
            "name": row.name,
            "description": row.description,
            "assemblyId": row.assemblyId,
            "createDateTime": None,
            "updateDateTime": None,
            "version": None,
            "variantCount": row.variantCount,
            "callCount": row.callCount,
            "sampleCount": row.sampleCount,
            "externalUrl": None,
            "info": {
                "accessType": row.accessType,
            }
        }
        BeaconDataset.append(asd)

    Organization = {
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

    Beacon = {
        'id': 'ega-beacon',
        'name': 'EGA Beacon',
        'apiVersion': '1.0.0',
        'organization': Organization,
        'description': 'This <a href=\"http://ga4gh.org/#/beacon\">Beacon</a> is based on the GA4GH Beacon\
         <a href=\"https://github.com/ga4gh/beacon-team/blob/develop/src/main/resources/avro/beacon.avdl\">API 0.4</a>',
        'version': 'v1',
        'welcomeUrl': 'https://ega-archive.org/beacon_web/',
        'alternativeUrl': 'https://ega-archive.org/beacon_web/',
        'createDateTime': '2018-07-25T00:00.000Z',
        'updateDateTime': None,
        'dataset': BeaconDataset,
        'sampleAlleleRequests': BeaconAlleleRequest,
        'info': {
            "size": ""
             }
    }
    return Beacon

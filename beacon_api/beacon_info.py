import beacon_api.models



def constructor():

    BeaconAllelRequest = [{
        "alternateBases": "A",
        "referenceBases": "C",
        "referenceName": "17",
        "start": 6689,
        "assemblyId": "GRCh37",
        "datasetIds": None,
        "includeDatasetResponses": False
    },
    {
        "alternateBases": "G",
        "referenceBases": "A",
        "referenceName": "1",
        "start": 14929,
        "assemblyId": "GRCh37",
        "datasetIds": [
        "EGAD00000000028"
        ],
        "includeDatasetResponses": "ALL"
    },
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
    db_object = beacon_api.models.Beacon_dataset_table
    db_table = db_object.query.all() # List of all the rows in the beacon_dataset_table
    for row_obj in db_table:
        asd = {
            "id": row_obj.id,
            "name": row_obj.name,
            "description": row_obj.description,
            "assemblyId": row_obj.assemblyId,
            "createDateTime": None,
            "updateDateTime": None,
            "version": None,
            "variantCount": row_obj.variantCount,
            "callCount": row_obj.callCount,
            "sampleCount": row_obj.sampleCount,
            "externalUrl": None,
            "info": {
                "accessType": row_obj.accessType,
            }
        }
        BeaconDataset.append(asd)

    Organization = {
        'id': 'EGA',
        'name': 'European Genome-Phenome Archive (EGA)',
        'description': 'The European Genome-phenome Archive (EGA) is a service for permanent archiving and sharing of all types of personally identifiable genetic and phenotypic data resulting from biomedical research projects.',
        'address': '',
        'welcomeUrl': 'https://ega-archive.org/',
        'contactUrl': 'mailto:beacon.ega@crg.eu',
        'logoUrl': 'https://ega-archive.org/images/logo.png',
        'info': None,
    }

    Beacon = {
        'id': 'ega-beacon',
        'name': 'EGA Beacon',
        'apiVersion': '0.4',
        'organization': Organization,
        'description': 'This <a href=\"http://ga4gh.org/#/beacon\">Beacon</a> is based on the GA4GH Beacon <a href=\"https://github.com/ga4gh/beacon-team/blob/develop/src/main/resources/avro/beacon.avdl\">API 0.4</a>',
        'version': 'v04',
        'welcomeUrl': 'https://ega-archive.org/beacon_web/',
        'alternativeUrl': 'https://ega-archive.org/beacon_web/',
        'createDateTime': '2015-06-15T00:00.000Z',
        'updateDateTime': None,
        'dataset': BeaconDataset,
        'sampleAlleleRequests': BeaconAllelRequest,
        'info': {
            "size": "60270153"
             }
    }
    return Beacon
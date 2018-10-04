from .. import __apiVersion__, __title__, __version__

example_dataset = [{"id": "string",
                    "name": "string",
                    "description": "string",
                    "assemblyId": "GRCh38",
                    "createDateTime": "2012-07-29 or 2017-01-17T20:33:40Z",
                    "updateDateTime": "2012-07-19 or 2017-01-17T20:33:40Z",
                    "version": "string",
                    "variantCount": 0,
                    "callCount": 0,
                    "sampleCount": 0,
                    "externalUrl": "http://example.org/wiki/Main_Page",
                    "info": [
                        {
                            "key": "string",
                            "value": "string"
                        }
                    ],

                    "dataUseConditions": {
                        "consentCodeDataUse": {
                            "primaryCategory": {
                                "code": "NRES",
                                "description": "string"
                            },
                            "secondaryCategories": [
                                {
                                    "code": "NRES",
                                    "description": "string"
                                }
                            ],
                            "requirements": [
                                {
                                    "code": "NRES",
                                    "description": "string"
                                }
                            ],
                            "version": 0.1
                        },
                        "adamDataUse": {
                            "header": {
                                "matrixName": "string",
                                "matrixVersion": "string",
                                "matrixReferences": [
                                    "string"
                                ],
                                "matrixProfileCreateDate": "2017-01-17T20:33:40Z",
                                "matrixProfileUpdates": [
                                    {
                                        "date": "2012-07-19 or 2017-01-17T20:33:40Z",
                                        "description": "string"
                                    }
                                ],
                                "resourceName": "string",
                                "resourceReferences": [
                                    "string"
                                ],
                                "resourceDescription": "string",
                                "resourceDataLevel": "UNKNOWN",
                                "resourceContactNames": [
                                    {
                                        "name": "string",
                                        "email": "string"
                                    }
                                ],
                                "resourceContactOrganisations": [
                                    "string"
                                ]
                            },
                            "profile": {
                                "country": "UNRESTRICTED",
                                "allowedCountries": [
                                    {
                                        "description": "string",
                                        "obligatory": True
                                    }
                                ],
                                "organisation": "UNRESTRICTED",
                                "allowedOrganisations": [
                                    {
                                        "description": "string",
                                        "obligatory": True
                                    }
                                ],
                                "nonProfitOrganisation": "UNRESTRICTED",
                                "allowedNonProfitOrganisations": [
                                    {
                                        "description": "string",
                                        "obligatory": True
                                    }
                                ],
                                "profitOrganisation": "UNRESTRICTED",
                                "allowedProfitOrganisations": [
                                    {
                                        "description": "string",
                                        "obligatory": True
                                    }
                                ],
                                "person": "UNRESTRICTED",
                                "allowedPersons": [
                                    {
                                        "description": "string",
                                        "obligatory": True
                                    }
                                ],
                                "academicProfessional": "UNRESTRICTED",
                                "allowedAcademicProfessionals": [
                                    {
                                        "description": "string",
                                        "obligatory": True
                                    }
                                ],
                                "clinicalProfessional": "UNRESTRICTED",
                                "allowedClinicalProfessionals": [
                                    {
                                        "description": "string",
                                        "obligatory": True
                                    }
                                ],
                                "profitProfessional": "UNRESTRICTED",
                                "allowedProfitProfessionals": [
                                    {
                                        "description": "string",
                                        "obligatory": True
                                    }
                                ],
                                "nonProfessional": "UNRESTRICTED",
                                "allowedNonProfessionals": [
                                    {
                                        "description": "string",
                                        "obligatory": True
                                    }
                                ],
                                "nonProfitPurpose": "UNRESTRICTED",
                                "allowedNonProfitPurposes": [
                                    {
                                        "description": "string",
                                        "obligatory": True
                                    }
                                ],
                                "profitPurpose": "UNRESTRICTED",
                                "allowedProfitPurposes": [
                                    {
                                        "description": "string",
                                        "obligatory": True
                                    }
                                ],
                                "researchPurpose": "UNRESTRICTED",
                                "allowedResearchPurposes": [
                                    {
                                        "description": "string",
                                        "obligatory": True
                                    }
                                ],
                                "allowedResearchProfiles": [
                                    {
                                        "type": "OTHER",
                                        "description": "string",
                                        "restriction": "UNRESTRICTED"
                                    }
                                ],
                                "clinicalPurpose": "UNRESTRICTED",
                                "allowedClinicalPurpose": [
                                    {
                                        "description": "string",
                                        "obligatory": True
                                    }
                                ],
                                "allowedClinicalProfiles": [
                                    {
                                        "type": "OTHER",
                                        "description": "string",
                                        "restriction": "UNRESTRICTED"
                                    }
                                ]
                            },
                            "terms": {
                                "noAuthorizationTerms": True,
                                "whichAuthorizationTerms": [
                                    "string"
                                ],
                                "noPublicationTerms": True,
                                "whichPublicationTerms": [
                                    "string"
                                ],
                                "noTimelineTerms": True,
                                "whichTimelineTerms": [
                                    "string"
                                ],
                                "noSecurityTerms": True,
                                "whichSecurityTerms": [
                                    "string"
                                ],
                                "noExpungingTerms": True,
                                "whichExpungingTerms": [
                                    "string"
                                ],
                                "noLinkingTerms": True,
                                "whichLinkingTerms": [
                                    "string"
                                ],
                                "noRecontactTerms": True,
                                "allowedRecontactTerms": [
                                    "string"
                                ],
                                "compulsoryRecontactTerms": [
                                    "string"
                                ],
                                "noIPClaimTerms": True,
                                "whichIPClaimTerms": [
                                    "string"
                                ],
                                "noReportingTerms": True,
                                "whichReportingTerms": [
                                    "string"
                                ],
                                "noCollaborationTerms": True,
                                "whichCollaborationTerms": [
                                    "string"
                                ],
                                "noPaymentTerms": True,
                                "whichPaymentTerms": [
                                    "string"
                                ]
                            },
                            "metaConditions": {
                                "sharingMode": "UNKNOWN",
                                "multipleObligationsRule": "MEET_ALL_OBLIGATIONS",
                                "noOtherConditions": True,
                                "whichOtherConditions": [
                                    "string"
                                ],
                                "sensitivePopulations": True,
                                "uniformConsent": True
                            }
                        }
                    }
                    }]


def beacon_info(host):
    """
    Construct the `Beacon` dict that the info end point will return.

    :type Beacon: Dict
    :return Beacon: A dict that contain all the information about the `Beacon`.
    """
    beacon_dataset = example_dataset

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

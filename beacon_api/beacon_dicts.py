
KeyValuePair = {
    'key': 'string',
    'value': 'string'
}

info = [KeyValuePair]

BeaconAllelRequest = [{
    "alternateBases": None,
    "referenceBases": None,
    "referenceName": "17",
    "start": 6689,
    "assemblyId": "GRCh37",
    "datasetIds": None,
    "includeDatasetResponses": False
},
{
    "alternateBases": None,
    "referenceBases": None,
    "referenceName": "1",
    "start": 1040026,
    "assemblyId": "GRCh37",
    "datasetIds": [
    "EGAD00001000740",
    "EGAD00001000741"
    ],
    "includeDatasetResponses": False
},
{
    "alternateBases": "C",
    "referenceBases": None,
    "referenceName": "1",
    "start": 1040026,
    "assemblyId": "GRCh37",
    "datasetIds": [
    "EGAD00001000740"
    ],
    "includeDatasetResponses": False
}
]

ConsentCodeDataUseConditionRequirement = {
    'code': '''Data use requirements:

NPU: not-for-profit use only - Use of the data is limited to not-for-profit organizations.
PUB: publication required - Requestor agrees to make results of studies using the data available to the larger scientific community.
COL-[XX]: collaboration required - Requestor must agree to collaboration with the primary study investigator(s).
RTN: return data to database/resource - Requestor must return derived/enriched data to the database/resource.
IRB: ethics approval required - Requestor must provide documentation of local IRB/REC approval.
GS-[XX]: geographical restrictions - Use of the data is limited to within [geographic region].
MOR-[XX]: publication moratorium/embargo - Requestor agrees not to publish results of studies until [date].
TS-[XX]: time limits on use - Use of data is approved for [x months].
US: user-specific restrictions - Use of data is limited to use by approved users.
PS: project-specific restrictions - Use of data is limited to use within an approved project.
IS: institution-specific restrictions - Use of data is limited to use within an approved institution.
Enum:
Array [ 11 ]
''',
    'description': 'string'
}

ConsentCodeDataUseConditionSecondary = {
    'code': '''Secondary data use categories:

RS-[XX]: other research-specific restrictions - Use of the data is limited to studies of [research type] (e.g., pediatric research).
RUO: research use only - Use of data is limited to research purposes (e.g., does not include its use in clinical care).
NMDS: no “general methods” research - Use of the data includes methods development research (e.g., development of software or algorithms) ONLY within the bounds of other data use limitations.
GSO: genetic studies only - Use of the data is limited to genetic studies only (i.e., no research using only the phenotype data).
Enum:
Array [ 4 ]
''',
    'description': 'string'
}

ConsentCodeDataUseConditionPrimary = {
    'code': '''Primary data use categories:

NRES: no restrictions - No restrictions on data use.
GRU(CC): general research use and clinical care - For health/medical/biomedical purposes and other biological research, including the study of population origins or ancestry.
HMB(CC): health/medical/biomedical research and clinical care - Use of the data is limited to health/medical/biomedical purposes, does not include the study of population origins or ancestry.
DS-XX: disease-specific research and clinical care - Use of the data must be related to [disease].
POA: population origins/ancestry research - Use of the data is limited to the study of population origins or ancestry.
Enum:
Array [ 5 ]
''',
    'description': 'string'
}

ConsentCodeDataUse = {
    'primaryCategory': ConsentCodeDataUseConditionPrimary,
    'secondaryCategories': ConsentCodeDataUseConditionSecondary,
    'requirements': ConsentCodeDataUseConditionRequirement,
    'version': 'string'
}

DataUseConditions = {
    'consentCodeDataUse': ConsentCodeDataUse
}

BeaconDataset = [{
    "id": "EGAD00001000433",
    "name": None,
    "description": "This sample set comprises cases of schizophrenia with additional cognitive measurements, collected in Aberdeen, Scotland.",
    "assemblyId": "grch37",
    "createDateTime": None,
    "updateDateTime": None,
    "version": None,
    "variantCount": 2086679,
    "callCount": None,
    "sampleCount": None,
    "externalUrl": None,
    "info": {
    "accessType": "CONTROLLED",
    "authorized": "false"
    }
},
{
    "id": "EGAD00001000614",
    "name": None,
    "description": "This sample set of UK origin consists of clinically identified subjects with Autism Spectrum Disorders, mostly without intellectual disability (i.e. Verbal IQ > 70). The subjects represent children and adults with Autism, Asperger syndrome or Atypical Autism, identified according to standardized research criteria (ADI-algorithm, ADOS). A minority has identified comorbid neurodevelopmental disorders (e.g. ADHD).",
    "assemblyId": "grch37",
    "createDateTime": None,
    "updateDateTime": None,
    "version": None,
    "variantCount": 2089776,
    "callCount": None,
    "sampleCount": None,
    "externalUrl": None,
    "info": {
    "accessType": "CONTROLLED",
    "authorized": "false"
    }
},
{
    "id": "EGAD00001000443",
    "name": None,
    "description": "The sample selection consists of subjects with schizophrenia (SZ), autism, or other psychoses all with mental retardation (learning disability).",
    "assemblyId": "grch37",
    "createDateTime": None,
    "updateDateTime": None,
    "version": None,
    "variantCount": 2070203,
    "callCount": None,
    "sampleCount": None,
    "externalUrl": None,
    "info": {
    "accessType": "CONTROLLED",
    "authorized": "false"
    }
},
{
    "id": "EGAD00001000740",
    "name": None,
    "description": "Low-coverage whole genome sequencing; variant calling, genotype calling and phasing",
    "assemblyId": "grch37",
    "createDateTime": None,
    "updateDateTime": None,
    "version": None,
    "variantCount": 41586925,
    "callCount": None,
    "sampleCount": None,
    "externalUrl": None,
    "info": {
    "accessType": "PUBLIC",
    "authorized": "true"
    }
},
{
    "id": "EGAD00001000613",
    "name": None,
    "description": "The MGAS (Molecular Genetics of Autism Study) samples are from a clinical sample seen by specialists at the Maudsley hospital and who have had detailed phenotypic assessments with ADI-R and ADOS.",
    "assemblyId": "grch37",
    "createDateTime": None,
    "updateDateTime": None,
    "version": None,
    "variantCount": 2069329,
    "callCount": None,
    "sampleCount": None,
    "externalUrl": None,
    "info": {
    "accessType": "CONTROLLED",
    "authorized": "false"
    }
},
{
    "id": "EGAD00001000430",
    "name": None,
    "description": "Two groups of samples with diagnosis of schizophrenia or schizoaffective disorder in the UK: cases with a positive family history of schizophrenia, either collected as sib-pairs or from multiplex kindreds. A second group consists mainly of samples that have been systematically collected within South Wales.",
    "assemblyId": "grch37",
    "createDateTime": None,
    "updateDateTime": None,
    "version": None,
    "variantCount": 2105114,
    "callCount": None,
    "sampleCount": None,
    "externalUrl": None,
    "info": {
    "accessType": "CONTROLLED",
    "authorized": "false"
    }
},
{
    "id": "EGAD00001000434",
    "name": None,
    "description": "The BioNED (Biomarkers for Childhood onset neuropsychiatric disorders) study has been carrying out detailed phenotypic assessments evaluating children with an autism spectrum disorder.",
    "assemblyId": "grch37",
    "createDateTime": None,
    "updateDateTime": None,
    "version": None,
    "variantCount": 2063632,
    "callCount": None,
    "sampleCount": None,
    "externalUrl": None,
    "info": {
    "accessType": "CONTROLLED",
    "authorized": "false"
    }
},
{
    "id": "EGAD00001000437",
    "name": None,
    "description": "The Tampere Autism sample set consists of samples from Finnish subjects with ASD (autism spectrum disorders) with IQs over 70 recruited from a clinical centre for the diagnosis and treatment of children with ASD.",
    "assemblyId": "grch37",
    "createDateTime": None,
    "updateDateTime": None,
    "version": None,
    "variantCount": 2052168,
    "callCount": None,
    "sampleCount": None,
    "externalUrl": None,
    "info": {
    "accessType": "CONTROLLED",
    "authorized": "false"
    }
},
{
    "id": "EGAD00001000439",
    "name": None,
    "description": "The entire sample collection consists of 2756 individuals from 458 families of whom 931 are diagnosed with schizophrenia spectrum disorder. Families outside Kuusamo (n=288) all had at least two affected siblings.",
    "assemblyId": "grch37",
    "createDateTime": None,
    "updateDateTime": None,
    "version": None,
    "variantCount": 2069984,
    "callCount": None,
    "sampleCount": None,
    "externalUrl": None,
    "info": {
    "accessType": "CONTROLLED",
    "authorized": "false"
    }
},
{
    "id": "EGAD00001000442",
    "name": None,
    "description": "Samples from three sources: the Genetics and Psychosis (GAP) set consists of samples from subjects with schizophrenia, ascertained as a new-onset sample; the Maudsley twin series consists of probands ascertained from the Maudsley Twin Register, defined as patients of multiple birth who had suffered psychotic symptoms; the Maudsley family study (MFS) consists of over 250 families who have a history of schizophrenia or bipolar disorder. ",
    "assemblyId": "grch37",
    "createDateTime": None,
    "updateDateTime": None,
    "version": None,
    "variantCount": 2076343,
    "callCount": None,
    "sampleCount": None,
    "externalUrl": None,
    "info": {
    "accessType": "CONTROLLED",
    "authorized": "false"
    }
}
]

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
    'description': 'This <a href=\"http://ga4gh.org/#/beacon\">Beacon</a> is based on the GA4GH Beacon <a href=\"https://github.com/ga4gh/beacon-team/blob/develop/src/main/resources/avro/beacon.avdl\">API 0.3</a>',
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
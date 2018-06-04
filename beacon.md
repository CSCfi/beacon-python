# Beacon API Specification v1.0.0

#### Name: Beacon
#### Description: A Beacon is a web service for genetic data sharing that can be queried for information about specific alleles.

#### Authors:
- ...

#### Publication Date: 
#### Version: 1.0.0

## Executive Summary

## Document Scope 

### Referenced External Standards
- ADA-M [version]
- Consent Codes [version]

## Design Principles


## API Protocol

HTTP Transport Protocol...

### Security...

## Beacon API Methods



## Beacon API Objects

### 1. Beacon 
##### Type: object
##### Required:
- id
- name
- apiVersion
- organization
- datasets
##### Properties:
##### Id:
- type: string
- description: Unique identifier of the beacon. Use reverse domain name notation.
- example: org.ga4gh.beacon
##### Name:
- type: string
- description: Name of the beacon.
##### ApiVersion:
- type: string
- description: Version of the API provided by the beacon.
- example: v0.3
##### Organization:
- [BeaconOrganization](#2.-beaconorganisation)
##### Description:
- type: string
- description: Description of the beacon.
##### Version:
- type: string
- description: Version of the beacon.
- example: v0.1
##### WelcomeUrl:
- type: string
- description: URL to the welcome page for this beacon (RFC 3986 format).
- example: http://example.org/wiki/Main_Page
##### AlternativeUrl:
- type: string
- description: Alternative URL to the API, e.g. a restricted version of this beacon (RFC 3986 format).
- example: http://example.org/wiki/Main_Page
##### CreateDateTime:
- type: string
- description: The time the beacon was created (ISO 8601 format).
- example: 2012-07-19 or 2017-01-17T20:33:40Z
##### UpdateDateTime:
- type: string
- description: The time the beacon was created (ISO 8601 format).
- example: 2012-07-19 or 2017-01-17T20:33:40Z
##### Datasets:
- description: Datasets served by the beacon. Any beacon should specify at least one dataset.
- type: array
- items:
- [BeaconDataset](#beacondataset)
##### SampleAlleleRequests:
- description: Examples of interesting queries, e.g. a few queries demonstrating different esponses.
- type: array
- items:
- [BeaconAlleleRequest](#4.-beaconallelerequest)
##### Info:
- description: Additional structured metadata, key-value pairs.
- type: array
- items:
- [KeyValuePair](#keyvaluepair)

### 2. BeaconOrganisation
    description: Organization owning the beacon.
    type: object
    required:
      - id
      - name
    properties:
      id:
        type: string
        description: 'Unique identifier of the organization.'
      name:
        type: string
        description: 'Name of the organization.'
      description:
        type: string
        description: 'Description of the organization.'
      address:
        type: string
        description: 'Address of the organization.'
      welcomeUrl:
        type: string
        description: 'URL of the website of the organization (RFC 3986 format).'
      contactUrl:
        type: string
        description: 'URL with the contact for the beacon operator/maintainer, e.g. link to a contact form (RFC 3986 format) or an email (RFC 2368 format).'
      logoUrl:
        type: string
        description: 'URL to the logo (PNG/JPG format) of the organization (RFC 3986 format).'
      info:
        description: Additional structured metadata, key-value pairs.
        type: array
        items:
          $ref: "#/definitions/KeyValuePair"    

### 3. BeaconDataset
    type: object
    required:
      - id
      - name
      - assemblyId
      - createDateTime
      - updateDateTime
    properties:
      id:
        type: string
        description: 'Unique identifier of the dataset.'
      name:
        type: string
        description: 'Name of the dataset.'
      assemblyId:
        description: 'Assembly identifier (GRC notation, e.g. `GRCh37`).'
        type: string
        example: GRCh38
      createDateTime:
        type: string
        description: 'The time the dataset was created (ISO 8601 format).'
        example: 2012-07-29 or 2017-01-17T20:33:40Z
      updateDateTime:
        type: string
        description: 'The time the dataset was created (ISO 8601 format).'
        example: 2012-07-19 or 2017-01-17T20:33:40Z
      version:
        type: string
        description: 'Version of the dataset.'
      variantCount:
        type: integer
        format: int64
        description: 'Total number of variants in the dataset.'
        minimum: 0
      callCount:
        type: integer
        format: int64
        description: 'Total number of calls in the dataset.'
        minimum: 0
      sampleCount:
        type: integer
        format: int64
        description: 'Total number of samples in the dataset.'
        minimum: 0
      externalUrl:
        type: string
        description: 'URL to an external system providing more dataset information (RFC 3986 format).'
        example: http://example.org/wiki/Main_Page
      info:
        description: Additional structured metadata, key-value pairs.
        type: array
        items:
          $ref: "#/definitions/KeyValuePair"    
      dataUseConditions:
        $ref: "#/definitions/DataUseConditions"

#### 4. BeaconAlleleRequest
    description: 'Allele request as interpreted by the beacon.'
    type: object
    required:
      - referenceName
      - start
      - startMin
      - startMax
      - endMin
      - endMax
      - referenceBases
      - alternateBases
      - assemblyId
    properties:
      referenceName:
        $ref: "#/definitions/Chromosome"
      start:
        description: 'Position, allele locus (0-based)'
        type: integer
        format: int64
        minimum: 0
      end:
        type: integer
      startMin:
        type: integer
      startMax:
        type: integer
      endMin:
        type: integer
      endMax:
        type: integer
      referenceBases:
        description: >-
          Reference bases for this variant (starting from `start`). For accepted values see the REF field in VCF 4.2 specification
        type: string
        enum:
          - A
          - C
          - G
          - T
          - N
      alternateBases:
        description: >-
          The bases that appear instead of the reference bases. For accepted values see the ALT field in VCF 4.2 specification
        type: string
      assemblyId:
        description: 'Assembly identifier (GRC notation, e.g. `GRCh37`).'
        type: string
        example: GRCh38
      datasetIds:
        description: >-
          Identifiers of datasets, as defined in `BeaconDataset`. If this field is null/not specified, all datasets should be queried.
        type: array
        items:
          type: string
      includeDatasetResponses:
        description: >-
          Indicator of whether responses for individual datasets
          (datasetAlleleResponses) should be included in the
          response (BeaconAlleleResponse) to this request or not. 
          If null (not specified), the default value of NONE is assumed.
        type: string
        enum: 
          - ALL
          - HIT
          - MISS
          - NONE

#### 5. BeaconAlleleResponse
    type: object
    required:
      - beaconId
    properties:
      beaconId:
        description: 'Identifier of the beacon, as defined in `Beacon`.'
        type: string
      apiVersion:
        description: 'Version of the API. If specified, the value must match `apiVersion` in Beacon'
        type: string
      exists:
        description: >-
          Indicator of whether the given allele was observed in any of the datasets queried. This should be non-null, unless there was an error, in which case `error` has to be non-null.
        type: boolean
      alleleRequest:
        $ref: "#/definitions/BeaconAlleleRequest"
      datasetAlleleResponses:
        description: 'Indicator of whether the given allele was  observed in individual datasets. This should be non-null if `includeDatasetResponses` in the corresponding `BeaconAlleleRequest` is true, and null otherwise.'
        type: array
        items:
          $ref: "#/definitions/BeaconDatasetAlleleResponse"
      error:
        $ref: '#/definitions/BeaconError' 

#### 5. BeaconDatasetAlleleDResponse
    type: object
    required:
      - datasetId
    properties:
      datasetId:
        type: string
        description: 'not provided'
      exists:
        description: >-
          Indicator of whether the given allele was observed in the dataset. This should be non-null, unless there was an error, in which case `error` has to be non-null.
        type: boolean
      error:
        $ref: '#/definitions/BeaconError' 
      frequency:
        type: number
        description: 'Frequency of this allele in the dataset. Between 0 and 1, inclusive.' 
        minimum: 0
        maximum: 1
      variantCount:
        type: integer
        format: int64
        description: 'Number of variants matching the allele request in the dataset.'
        minimum: 0
      callCount:
        type: integer
        format: int64
        description: 'Number of calls matching the allele request in the dataset.'
        minimum: 0
      sampleCount:
        type: integer
        format: int64
        description: 'Number of samples matching the allele request in the dataset'
        minimum: 0
      note:
        type: string
        description: 'Additional note or description of the response.'
      externalUrl:
        type: string
        description: 'URL to an external system, such as a secured beacon or a system providing more information about a given allele (RFC 3986 format).'
      info:
        description: 'Additional structured metadata, key-value pairs.'
        type: array
        items:
          $ref: "#/definitions/KeyValuePair"      

## Beacon API Example

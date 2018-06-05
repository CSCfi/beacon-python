# Beacon API Specification v1.0.0

#### Name: Beacon
#### Description: A Beacon is a web service for genetic data sharing that can be queried for information about specific alleles.

#### Authors:
- Kasper Keinänen

#### Publication Date: 
xx.06.2018
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
#### Type: object
#### Required:
- [Id](#id:)
- [Name](#name:)
- [ApiVersion](#apiversion:)
- [Organization](#organization:)
- [Datasets](#datasets:)
#### Properties:
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
- [BeaconDataset](#3.-beacondataset)
##### SampleAlleleRequests:
- description: Examples of interesting queries, e.g. a few queries demonstrating different esponses.
- type: array
- items:
- [BeaconAlleleRequest](#4.-beaconallelerequest)
##### Info:
- description: Additional structured metadata, key-value pairs.
- type: array
- items:
- [KeyValuePair](#7.-keyvaluepair:)






### 2. BeaconOrganisation
#### Description: Organization owning the beacon.
#### Type: object
#### Required:
- [id](#id:)
- [name](#name:)
#### Properties:
##### id:
- type: string
- description: 'Unique identifier of the organization.'
##### name:
- type: string
- description: 'Name of the organization.'
##### description:
- type: string
- description: 'Description of the organization.'
##### address:
- type: string
- description: 'Address of the organization.'
##### welcomeUrl:
- type: string
- description: 'URL of the website of the organization (RFC 3986 format).'
##### contactUrl:
- type: string
- description: 'URL with the contact for the beacon operator/maintainer, e.g. link to a contact form (RFC 3986 format) or an email (RFC 2368 format).'
##### logoUrl:
- type: string
- description: 'URL to the logo (PNG/JPG format) of the organization (RFC 3986 format).'
##### info:
- description: Additional structured metadata, key-value pairs.
- type: array
- items:
    - [KeyValuePair](#7.-keyvaluepair:)    
    
    
    
    
    
    

### 3. BeaconDataset
#### Type: object
#### Required:
- [Id](#id:)
- [Name](#name:)
- [AssemblyId](#assemblyId:)
- [CreateDateTime](#createDateTime:)
- [UpdateDateTime](#updateDateTime:)
#### Properties:
##### Id:
- type: string
- description: 'Unique identifier of the dataset.'
##### Name:
- type: string
- description: 'Name of the dataset.'
##### AssemblyId:
- description: 'Assembly identifier (GRC notation, e.g. `GRCh37`).'
- type: string
- example: GRCh38
##### CreateDateTime:
- type: string
- description: 'The time the dataset was created (ISO 8601 format).'
- example: 2012-07-29 or 2017-01-17T20:33:40Z
##### UpdateDateTime:
- type: string
- description: 'The time the dataset was created (ISO 8601 format).'
- example: 2012-07-19 or 2017-01-17T20:33:40Z
##### Version:
- type: string
- description: 'Version of the dataset.'
##### VariantCount:
- type: integer
- format: int64
- description: 'Total number of variants in the dataset.'
- minimum: 0
##### CallCount:
- type: integer
- format: int64
- description: 'Total number of calls in the dataset.'
- minimum: 0
##### SampleCount:
- type: integer
- format: int64
- description: 'Total number of samples in the dataset.'
- minimum: 0
##### ExternalUrl:
- type: string
- description: 'URL to an external system providing more dataset information (RFC 3986 format).'
- example: http://example.org/wiki/Main_Page
##### Info:
- description: Additional structured metadata, key-value pairs.
- type: array
- items:
    - [KeyValuePair](#7.-keyvaluepair:)    
##### DataUseConditions:
- [DataUseConditions](#dataUseConditions:)/////////////////////////////////////////////////////







### 4. BeaconAlleleRequest
#### Description: 'Allele request as interpreted by the beacon.'
#### Type: object
#### Required:
- [referenceName](#referencename:)
- [start](#start:)
- [startMin](#startmin:)
- [startMax](#startmax:)
- [endMin](#endmin:)
- [endMax](#endmax:)
- [referenceBases](#referencebases:)
- [alternateBases](#alternatebases:)
- [assemblyId](#assemblyid:)
#### Properties:
##### referenceName:
- [Chromosome](#9.-chromosome:)
##### start:
- description: 'Position, allele locus (0-based)'
- type: integer
- format: int64
- minimum: 0
##### end:
- type: integer
##### startMin:
- type: integer
##### startMax:
- type: integer
##### endMin:
- type: integer
##### endMax:
- type: integer
##### referenceBases:
- description: Reference bases for this variant (starting from `start`). For accepted values see the REF field in VCF 4.2 specification
- type: string
- enum:
     - A
     - C
     - G
     - T
     - N
##### alternateBases:
- description: The bases that appear instead of the reference bases. For accepted values see the ALT field in VCF 4.2 specification
- type: string
##### assemblyId:
- description: 'Assembly identifier (GRC notation, e.g. `GRCh37`).'
- type: string
- example: GRCh38
##### datasetIds:
- description: Identifiers of datasets, as defined in `BeaconDataset`. If this field is null/not specified, all datasets should be queried.
- type: array
- items:
    - type: string
##### includeDatasetResponses:
- description: Indicator of whether responses for individual datasets
          (datasetAlleleResponses) should be included in the
          response (BeaconAlleleResponse) to this request or not. 
          If null (not specified), the default value of NONE is assumed.
- type: string
- enum: 
     - ALL
     - HIT
     - MISS
     - NONE






### 5. BeaconAlleleResponse
#### Type: object
#### Required:
- beaconId
#### Properties:
##### beaconId:
- description: 'Identifier of the beacon, as defined in `Beacon`.'
- type: string
##### apiVersion:
- description: 'Version of the API. If specified, the value must match `apiVersion` in Beacon'
- type: string
##### exists:
- description: Indicator of whether the given allele was observed in any of the datasets queried. This should be non-null, unless there was an error, in which case `error` has to be non-null.
- type: boolean
##### alleleRequest:
- [BeaconAlleleRequest](#4.-beaconallelerequest)
##### datasetAlleleResponses:
- description: 'Indicator of whether the given allele was  observed in individual datasets. This should be non-null if `includeDatasetResponses` in the corresponding `BeaconAlleleRequest` is true, and null otherwise.'
- type: array
- items:
    - $ref: "#/definitions/BeaconDatasetAlleleResponse"
##### error:
- [BeaconError](#8.-beaconerror:) 
        
        
      
      
        

### 6. BeaconDatasetAlleleDResponse
#### Type: object
#### Required:
- datasetId
#### Properties:
##### datasetId:
- type: string
- description: 'not provided'
##### exists:
- description: Indicator of whether the given allele was observed in the dataset. This should be non-null, unless there was an error, in which case `error` has to be non-null.
- type: boolean
##### error:
- [BeaconError](#8.-beaconerror:) 
##### frequency:
- type: number
- description: 'Frequency of this allele in the dataset. Between 0 and 1, inclusive.' 
- minimum: 0
- maximum: 1
##### variantCount:
- type: integer
- format: int64
- description: 'Number of variants matching the allele request in the dataset.'
- minimum: 0
##### callCount:
- type: integer
- format: int64
- description: 'Number of calls matching the allele request in the dataset.'
- minimum: 0
##### sampleCount:
- type: integer
- format: int64
- description: 'Number of samples matching the allele request in the dataset'
- minimum: 0
##### note:
- type: string
- description: 'Additional note or description of the response.'
##### externalUrl:
- type: string
- description: 'URL to an external system, such as a secured beacon or a system providing more information about a given allele (RFC 3986 format).'
##### info:
- description: 'Additional structured metadata, key-value pairs.'
- type: array
- items:
     - [KeyValuePair](#7.-keyvaluepair:) 
     



### 7. KeyValuePair:
#### Type: object
#### Required:
- key
- value
#### Properties:
##### key:
- type: string
##### value:
- type: string 




### 8. BeaconError:
#### Description: Beacon-specific error. This should be non-null in exceptional situations only, in which case `exists` has to be null.
#### Type: object
#### Required:
- errorCode
#### Properties:
##### errorCode:
- type: integer
- format: int32
##### errorMessage:
- type: string





### 9. Chromosome:
#### Description: 'Reference name (chromosome). Accepting values 1-22, X, Y.'
#### Type: string
#### Enum:
- 1
- 2
- 3
- 4
- 5
- 6
- 7
- 8
- 9
- 10
- 11
- 12
- 13
- 14
- 15
- 16
- 17
- 18
- 19
- 20
- 21
- 22
- X 
- Y

## Beacon API Example
    

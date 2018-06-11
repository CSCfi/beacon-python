# Beacon API Specification v1.0.0

#### Name: Beacon API
#### Description: A Beacon is a web service for genetic data sharing that can be queried for information about specific alleles.

#### Authors:
- Ilkka Lappalainen
- Jordi Rambla
- Juha Törnroos
- Kasper Keinänen
- Marc Fiume
- Michael Baudis
- Miro Cupack
- Sabela de la Torre
- Saif 



#### Publication Date: xx.06.2018
#### Version: 1.0.0

## Executive Summary
The main purpose of Beacon is to make genetic data discoverable without a need to apply access to datasets beforehand. With Beacon it is possible to make simple queries to the datasets and discover interesting datasets. If interesting dataset is found Beacon will point to appropriate place to apply dataset permissions (e.g. to EGA).    

## Document Scope 
This document explains what are the design principles in Beacon API, how protocol works, what methods are offered by the API and shows API works in practise by providing examples. This document does not editorialise how Beacon API should be implemented. However there are implementations of this API, such as [ELIXIR Beacon reference implementation](https://github.com/ga4gh-beacon/beacon-elixir).  

### Referenced External Standards
- [ADA-M](https://github.com/ga4gh/ADA-M) 
- [GA4GH Consent Codes](https://github.com/ga4gh/ga4gh-consent-policy)

## Design Principles
Beacon provides REST API on top of HTTP protocol.



## API Protocol
The Beacon API has two endpoints:

#### - `/`
The `/` endpoint has only one method, the `get()` method.
about the API.

#### - `/query`
The `/query` endpoint has two methods, the `get()` and the `post()`.

### Security
Three level access tiers: open, regisered and controlled. 

## Beacon API Methods

#### Beacon `/` endpoint:
##### - METHOD: `GET`
The `get()` method uses the HTTP protocol 'GET' to returns a Json object of all the necessary info on the beacon and the Api. It
uses the `/` path and only serves an information giver. The parameters that the method returns and their descriptions
can be found under the title: [Beacon]()

        
#### Beacon `/query` endpoint:
##### - METHOD: `GET`
The `get()` method uses the HTTP
protocol 'GET' to return a Json object. The object contains the `alleleRequest` that was submitted, the `datasetAlleleResponse`
that was received, some general info on the api and the parameter `exists`. The `exists` parameter is the answer from the
query that tells the user if the allele was found or not.


##### - METHOD: `POST`
The `post()` method runs the same code as the `get()` method but uses the HTTP protocol `POST` instead. The main difference
between the methods is that the parameters are not sent in the URL. This is more secure because the `GET` requests URLs get
logged and then if you use the `POST` instead, you dont reveal the parameters that you query with.


                

    

## Beacon API Objects

### 1. Beacon 
#### Type: 
object
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
#### Description: 
Organization owning the beacon.
#### Type: 
object
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
#### Type: 
object
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
#### Description: 
'Allele request as interpreted by the beacon.'
#### Type: 
object
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
#### Type: 
object
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
#### Type: 
object
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
#### Type: 
object
#### Required:
- key
- value
#### Properties:
##### key:
- type: string
##### value:
- type: string 




### 8. BeaconError:
#### Description: 
Beacon-specific error. This should be non-null in exceptional situations only, in which case `exists` has to be null.
#### Type: 
object
#### Required:
- errorCode
#### Properties:
##### errorCode:
- type: integer
- format: int32
##### errorMessage:
- type: string





### 9. Chromosome:
#### Description: 
'Reference name (chromosome). Accepting values 1-22, X, Y.'
#### Type: 
string
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
#### - /
Example of how to use the GET method in the "/" path:    
`curl -v http://localhost:5000/` 
    
    > GET / HTTP/1.1
    > Host: localhost:5000
    > User-Agent: curl/7.54.0
    > Accept: */*
    > 
    * HTTP 1.0, assume close after body
    < HTTP/1.0 200 OK
    < Content-Type: application/json
    < Content-Length: 2391
    < Server: Werkzeug/0.14.1 Python/3.6.5
    < Date: Fri, 08 Jun 2018 12:07:36 GMT
    < 
    {
      "alternativeUrl": "https://ega-archive.org/beacon_web/", 
      "apiVersion": "0.4", 
      "createDateTime": "2015-06-15T00:00.000Z", 
      "dataset": [
        {
          "assemblyId": "grch37", 
          "callCount": 74, 
          "createDateTime": null, 
          "description": "This sample set comprises cases of schizophrenia with additional cognitive measurements, collected in Aberdeen, Scotland.", 
          "externalUrl": null, 
          "id": "EGAD00000000028", 
          "info": {
            "accessType": "PUBLIC", 
            "authorized": "false"
          }, 
          "name": null, 
          "sampleCount": 1, 
          "updateDateTime": null, 
          "variantCount": 74, 
          "version": null
        }
      ], 
      "description": "This <a href=\"http://ga4gh.org/#/beacon\">Beacon</a> is based on the GA4GH Beacon <a href=\"https://github.com/ga4gh/beacon-team/blob/develop/src/main/resources/avro/beacon.avdl\">API 0.4</a>", 
      "id": "ega-beacon", 
      "info": {
        "size": "60270153"
      }, 
      "name": "EGA Beacon", 
      "organization": {
        "address": "", 
        "contactUrl": "mailto:beacon.ega@crg.eu", 
        "description": "The European Genome-phenome Archive (EGA) is a service for permanent archiving and sharing of all types of personally identifiable genetic and phenotypic data resulting from biomedical research projects.", 
        "id": "EGA", 
        "info": null, 
        "logoUrl": "https://ega-archive.org/images/logo.png", 
        "name": "European Genome-Phenome Archive (EGA)", 
        "welcomeUrl": "https://ega-archive.org/"
      }, 
      "sampleAlleleRequests": [
        {
          "alternateBases": "A", 
          "assemblyId": "GRCh37", 
          "datasetIds": null, 
          "includeDatasetResponses": false, 
          "referenceBases": "C", 
          "referenceName": "17", 
          "start": 6689
        }, 
        {
          "alternateBases": "G", 
          "assemblyId": "GRCh37", 
          "datasetIds": [
            "EGAD00000000028"
          ], 
          "includeDatasetResponses": "ALL", 
          "referenceBases": "A", 
          "referenceName": "1", 
          "start": 14929
        }, 
        {
          "alternateBases": "CCCCT", 
          "assemblyId": "GRCh37", 
          "datasetIds": [
            "EGAD00001000740", 
            "EGAD00001000741"
          ], 
          "includeDatasetResponses": "HIT", 
          "referenceBases": "C", 
          "referenceName": "1", 
          "start": 866510
        }
      ], 
      "updateDateTime": null, 
      "version": "v04", 
      "welcomeUrl": "https://ega-archive.org/beacon_web/"
    }
    * Closing connection 0
#### - /query
Example of how to use the GET method in the "/query" path:

    curl -v 'http://localhost:5000/query?referenceName=1&start=0&end=0&startMin=28000000&startMax=29000000&endMin=28000000&endMax=29000000&referenceBases=A&alternateBases=T&assemblyId=GRCh37&datasetIds=EGAD00000000028&includeDatasetResponses=ALL'
######
    
    > GET /query?referenceName=1&start=0&end=0&startMin=28000000&startMax=29000000&endMin=28000000&endMax=29000000&referenceBases=A&alternateBases=T&assemblyId=GRCh37&datasetIds=EGAD00000000028&includeDatasetResponses=ALL HTTP/1.1
    > Host: localhost:5000
    > User-Agent: curl/7.54.0
    > Accept: */*
    > 
    * HTTP 1.0, assume close after body
    < HTTP/1.0 200 OK
    < Content-Type: application/json
    < Content-Length: 1078
    < Server: Werkzeug/0.14.1 Python/3.6.5
    < Date: Mon, 11 Jun 2018 07:29:26 GMT
    < 
    {
        "beaconId": "ega-beacon",
        "apiVersion": "0.4",
        "exists": true,
        "error": null,
        "allelRequest": {
            "referenceName": "1",
            "start": 0,
            "startMin": 28000000,
            "startMax": 29000000,
            "end": 0,
            "endMin": 28000000,
            "endMax": 29000000,
            "referenceBases": "A",
            "alternateBases": "T",
            "assemblyId": "GRCh37",
            "datasetIds": [
                "EGAD00000000028"
            ],
            "includeDatasetResponses": "ALL"
        },
        "datasetAllelResponses": [
            {
                "datasetId": "EGAD00000000028",
                "exists": true,
                "frequency": 0.5,
                "variantCount": 1,
                "callCount": 1,
                "sampleCount": 1,
                "note": "This sample set comprises cases of schizophrenia with additional cognitive measurements, collected in Aberdeen, Scotland.",
                "externalUrl": null,
                "info": {
                    "accessType": "PUBLIC",
                    "authorized": "false"
                },
                "error": null
            }
        ]
    }
    * Closing connection 0
    
    
######
Example of how to use the POST method in the "/query" path:
   
    curl -v -d "referenceName=1&start=14929&referenceBases=A&alternateBases=G&assemblyId=GRCh37&datasetIds=EGAD00000000028&includeDatsetResponses=ALL" http://localhost:5000/query
######

    > POST /query HTTP/1.1
    > Host: localhost:5000
    > User-Agent: curl/7.54.0
    > Accept: */*
    > Content-Length: 133
    > Content-Type: application/x-www-form-urlencoded
    > 
    * upload completely sent off: 133 out of 133 bytes
    * HTTP 1.0, assume close after body
    < HTTP/1.0 200 OK
    < Content-Type: application/json
    < Content-Length: 1056
    < Server: Werkzeug/0.14.1 Python/3.6.5
    < Date: Mon, 11 Jun 2018 07:15:48 GMT
    < 
    {
        "beaconId": "ega-beacon",
        "apiVersion": "0.4",
        "exists": true,
        "error": null,
        "alleleRequest": {
            "referenceName": "1",
            "start": 14929,
            "startMin": 0,
            "startMax": 0,
            "end": 0,
            "endMin": 0,
            "endMax": 0,
            "referenceBases": "A",
            "alternateBases": "G",
            "assemblyId": "GRCh37",
            "datasetIds": [
                "EGAD00000000028"
            ],
            "includeDatasetResponses": "ALL"
        },
        "datasetAlleleResponses": [
            {
                "datasetId": "EGAD00000000028",
                "exists": true,
                "frequency": 0.5,
                "variantCount": 1,
                "callCount": 1,
                "sampleCount": 1,
                "note": "This sample set comprises cases of schizophrenia with additional cognitive measurements, collected in Aberdeen, Scotland.",
                "externalUrl": null,
                "info": {
                    "accessType": "PUBLIC",
                    "authorized": "false"
                },
                "error": null
            }
        ]
    }
    * Closing connection 0
    
    


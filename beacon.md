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
can be found under the title: [Beacon](#beacon)

        
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

### <a name="beacon"></a>1. Beacon

(Required properties are marked with *)

|Properties|Description|Type|Example|
|---|---|:---:|---|
|**id***|Unique identifier of the beacon. Use reverse domain name notation.|string|org.ga4gh.beacon|
|**name***|Name of the beacon|string|-|
|**apiVersion***|Version of the API provided by the beacon.|string|v0.3|
|**organisation***|asd|object|[Organization](#organisation)|
|**datasets***|Datasets served by the beacon. Any beacon should specify at least one dataset.|array|items --> [BeaconDataset](#beacondataset)|
|description|Description of the beacon.|string|-|
|version|Version of the beacon.|string|v0.1|
|welcomeUrl|URL to the welcome page for this beacon (RFC 3986 format).|string|'http://example.org/wiki/Main_Page'|
|alternativeUrl|Alternative URL to the API, e.g. a restricted version of this beacon (RFC 3986 format).|string|'http://example.org/wiki/Main_Page'|
|createDateTime|The time the beacon was created (ISO 8601 format).|string|'2012-07-19 or 2017-01-17T20:33:40Z'|
|updateDateTime|The time the beacon was updated in (ISO 8601 format).|string|'2012-07-19 or 2017-01-17T20:33:40Z'|
|sampleAlleleRequests|Examples of interesting queries, e.g. a few queries demonstrating different responses.|array|items --> [BeaconAlleleRequest](#beaconallelrequest)|
|info|'Additional structured metadata, key-value pairs.'|array|items --> [KeyValuePair](#keyvaluepair)|


          
### <a name="beaconallelrequest"></a>2. BeaconAlleleRequest

>**Allele request as interpreted by the beacon.**

(Required properties are marked with *)

(Either of two is Required ~)

|Properties|Description|Type|Example|
|---|---|:---:|---|
|**referenceName***|Reference name (chromosome). Accepting values 1-22, X, Y.|string|`'1'`|
|**referenceBases***|Reference bases for this variant (starting from `start`). Accepted values: [ACGT]* When querying for variants without specific base alterations (e.g. imprecise structural variants with separate variant_type as well as start_min & end_min ... parameters), the use of a single "N" value is required.<br/>See the REF field in [VCF 4.2 specification](https://samtools.github.io/hts-specs/VCFv4.2.pdf).|string|`'G'`|
|**assemblyId***|Assembly identifier|string|`'GRCh38'`|
|start~|<p>* `start` only:<br />- for single positions, e.g. the start of a specified sequence alteration where the size is given through the specified alternateBases<br />- typical use are queries for SNV and small InDels<br />- the use of `start` without an `end` parameter requires the use of `referenceBases`<br />* `start` and `end:<br /> - special use case for exactly determined structural changes |integer|`345233`|
|startMin~|Minimum start coordinate<br />* `startMin` + `startMax` + `endMin` + `endMax`:<br />- for querying imprecise positions (e.g. identifying all structural variants starting anywhere between `startMin` <-> `startMax`, and ending anywhere between `endMin` <-> `endMax`<br />- single or double sided precise matches can be achieved by setting `startMin` = `startMax` OR `endMin` = `endMax<br/> <br/>For more information on range querys, see: [Beacon-Querys](https://github.com/ga4gh-beacon/specification/wiki/Beacon-Queries#range-queries-and-structural-variants)|integer|`23433`|
|startMax|Maximum start coordinate. See `startMin`.|integer|`23450`|
|end|Precise end coordinate. See `start`.|integer|`455635`|
|endMin|Minimum end coordinate. See `startMin`.|integer|`23500`|
|endMax|Maximum end coordinate. See `startMin.|integer|`23520`|
|alternateBases~|The bases that appear instead of the reference bases. Accepted values: [ACGT]* or N.<br /> <br/>Symbolic ALT alleles (DEL, INS, DUP, INV, CNV, DUP:TANDEM, DEL:ME, INS:ME) will be represented in variantType.<br/> <br/> See the ALT field in [VCF 4.2 specification](https://samtools.github.io/hts-specs/VCFv4.2.pdf)<br/> <br/>*Either `alternateBases` OR `varianType` is REQUIRED*|string|`'A'`|
|variantType~|The `variantType` is used to denote e.g. structural variants. See [variantType gossary](#variantType-glossary) for more.<br/> <br/>*Either `alternateBases` OR `varianType is REQUIRED*|string|`'INS'`|
|datasetIds|Identifiers of datasets, as defined in `BeaconDataset`. If this field is null/not specified, all datasets should be queried.|array|`['dataset1', 'dataset2']`|
|includeDatasetResponses|Indicator of whether responses for individual datasets (`datasetAlleleResponses`) should be included in the response (`BeaconAlleleResponse) to this request or not. If null (not specified), the default value of NONE is assumed.<br/> <br/>Accepted values : ['ALL', 'HIT', 'MISS', 'NONE']|string|`'ALL'`|

### <a name="variantType-glossary"></a>VariantType glossary:

|Abbreviation|Description|
|:---:|---|
|INS|**Insertion**: The insertion of a single stretch of DNA sequence into a specific position.|
|DEL|**Deletion**: The deletion of a single stretch of DNA sequence from a position.|
|DUP|**Duplication**: The copying of a stretch of DNA sequence and adding it to the end of the sequence.|
|INV|**Inversion**: Taking a specific stretch from a DNA sequence and inverting it (flipping it) and adding it to the same position.|
|CNV|**Copy Number Variation**: When a section of the DNA sequense is repeated.|
|SNP|**Single Nucleotide Polymorphism**: The substitution of a single base-pair.  e.g. 'A' --> 'C'. |

![alt text](https://www.ebi.ac.uk/training/online/sites/ebi.ac.uk.training.online/files/resize/GenVar_Fig_Structural_variation-600x391.png)
![](https://www.ebi.ac.uk/training/online/sites/ebi.ac.uk.training.online/files/resize/GenVar_Fig_SNP_2-750x112.png)


### <a name="beaconallelresponse"></a>3. BeaconAlleleResponse
>**The response to the given query.**

(Required properties are marked with *)

|Properties|Description|Type|Example|
|---|---|:---:|---|
|**beaconId***|Identifier of the beacon, as defined in `Beacon`.|string|-|
|apiVersion|Version of the API. If specified, the value must match `apiVersion` in Beacon|string|-|
|exists|Indicator of whether the given allele was observed in any of the datasets queried. This should be non-null, unless there was an error, in which case `error` has to be non-null.|boolean|`TRUE`|
|alleleRequest|The request that is sent to the Beacon.|object|[BeaconAlleleRequest](#beaconallelrequest)|
|datasetAlleleResponses|The response that the user receives from the Beacon|object|[BeaconDatasetAlleleResponse](#beacondatasetallelresponse)|
|error|The error message and the appropriate HTTP status code|object|[Error](#error)|





### <a name="beaconorganisation"></a>4. BeaconOrganization

>**The organization owning the beacon.**

(Required properties are marked with *)

|Properties|Description|Type|Example|
|---|---|:---:|---|
|**id***|Unique identifier of the organization.|string|-|
|**name***|Name of the organization.|string|-|
|description|Description of the organization.|string|-|
|address|Address of the organization.|string|-|
|welcomeUrl|URL of the website of the organization (RFC 3986 format).|string|-|
|contactUrl|URL with the contact for the beacon operator/maintainer, e.g. link to a contact form (RFC 3986 format) or an email (RFC 2368 format).|string|-|
|logoUrl|URL to the logo (PNG/JPG format) of the organization (RFC 3986 format).|string|-|
|info|Additional structured metadata, key-value pairs.|string|[KeyValuePair](#keyvaluepair)|


### <a name="beacondataset"></a>5. BeaconDataset

>**THe individual datasets that the user can query.**

(Required properties are marked with *)

|Properties|Description|Type|Example|
|---|---|:---:|---|
|**id***|Unique identifier of the dataset.|string|-|
|**name***|Name of the dataset.|string|-|
|**assemblyId***|Assembly identifier|string|`'GRCh38'`|
|**createDateTime***|The time the dataset was created (ISO 8601 format).|string|`'2012-07-29 or 2017-01-17T20:33:40Z'`|
|**updateDateTime***|The time the dataset was updated in (ISO 8601 format).|string|`'2012-07-19 or 2017-01-17T20:33:40Z'`|
|description|Description of the dataset.|string|-|
|version|Version of the dataset.|string|-|
|variantCount|Total number of variants in the dataset.|integer|`230453`|
|callCount|Total number of calls in the dataset.|integer|`213454`|
|sampleCount|Total number of samples in the dataset.|integer|`13`|
|externalUrl|URL to an external system providing more dataset information (RFC 3986 format).|string|-|
|info|Additional structured metadata, key-value pairs.|array|[KeyValuePair](#keyvaluepair)|
|dataUseConditions|Data use conditions ruling this dataset.|object|[DataUseConditions](#datauseconditions)|



### <a name="beacondatasetallelresponse"></a>6. BeaconDatasetAlleleResponse

>**The individual responces from the different datasets.**

(Required properties are marked with *)

|Properties|Description|Type|Example|
|---|---|:---:|---|
|**datasetId***|Unique identifier of the dataset.|string|-|
|exists|Indicator of whether the given allele was observed in the dataset. This should be non-null, unless there was an error, in which case `error` has to be non-null.|boolean|`TRUE`|
|error|The error message and the appropriate HTTP status code|object|[BeaconError](beaconerror)|
|frequency|Frequency of this allele in the dataset. Between 0 and 1, inclusive.|float|`0.07`|
|variantCount|Number of variants matching the allele request in the dataset.|integer|`2`|
|callCount|Number of calls matching the allele request in the dataset.|integer|`3`|
|sampleCount|Number of samples matching the allele request in the dataset|integer|`1`|
|note|Additional note or description of the response.|string|-|
|externalUrl|URL to an external system, such as a secured beacon or a system providing more information about a given allele (RFC 3986 format).|string|-|
|info|Additional structured metadata, key-value pairs.|array|[KeyValuePair](keyvaluepair)|



### <a name="beaconerror"></a>7.  BeaconError

>**Beacon-specific error. This should be non-null in exceptional situations only, in which case `exists` has to be null.**
>
>**See [Error](#error) for more information on the Beacon-specific errors.**

(Required properties are marked with *)

|Properties|Description|Type|Example|
|---|---|:---:|---|
|**errorCode***|The HTTP status code that is given in the event that an error occurs|integer|`400`|
|errorMessage|The error message explaining why the error occurred|string|`Missing mandatory parameter referenceName`|


### <a name="keyvaluepair"></a>8. KeyValuePair

>**Additional structured metadata**

(Required properties are marked with *)


|Properties|Description|Type|Example|
|---|---|:---:|---|
|**key***|-|string|-|
|**value***|-|string|-|


### <a name="datausecondition"></a>9. DataUseConditions

>**Data use conditions ruling this dataset.**

(Required properties are marked with *)

|Properties|Description|Type|Example|
|---|---|:---:|---|
|*consentCodeDataUse**|The consent code for the use of data.|object|[consentCodeDatause](https://raw.githubusercontent.com/ga4gh/ga4gh-consent-policy/806ea53cffacb2055c3639f0fc9783f0dcd8cb02/consent_code.yaml#/components/schemas/ConsentCodeDataUse)|
|*adamDataUse**|The Automatable Discovery and Access Matrix (ADA-M) provides a standardized way to unambiguously represent the conditions related to data discovery and access. |object|[ADA-M]() |



### <a name="adamdatause"></a>10. AdamDataUse

>**The Automatable Discovery and Access Matrix (ADA-M) provides a standardized way to unambiguously represent the conditions related to data discovery and access.**

(Required properties are marked with *)

|Properties|Description|Type|Example|
|---|---|:---:|---|
|**header***|General description of what the data is.|object|[AdamHeader](https://raw.githubusercontent.com/sdelatorrep/ADA-M/openapi_v2.0/adam.yaml#/definitions/AdamHeader)|
|**profile***|Profile of the data.|object|[AdamProfile](https://raw.githubusercontent.com/sdelatorrep/ADA-M/openapi_v2.0/adam.yaml#/definitions/AdamProfile)|
|**terms***|Terms related to the use of the data.|object|[AdamTerms](https://raw.githubusercontent.com/sdelatorrep/ADA-M/openapi_v2.0/adam.yaml#/definitions/AdamTerms)|
|**metaConditions***|Special conditions.|object|[AdamMtaConditions](https://raw.githubusercontent.com/sdelatorrep/ADA-M/openapi_v2.0/adam.yaml#/definitions/AdamMetaConditions)|


## <a name="errors"></a>Errors

The server MUST respond with the appropriate HTTP status code when an error condition is detected. In the case of transient 
server errors, (e.g., 500 and other 5xx status codes), the client SHOULD implement appropriate retry logic.

For errors that are specific to the Beacon API, the response will be one of the HTTP status codes represented in the table below. 
The response body SHOULD be a JSON object (content-type application/json) providing machine-readable information 
about the nature of the error, along with a human-readable description. 


The following errors types are defined: 

| Error type | HTTP status code | Description |
|---|:---:|---|
|Bad request|400|Mandatory parameters are missing or they are invalid|
|Unauthorized|401|When an unauthenticated user is trying to access a protected resource|
|Forbidden|403|The resource is protected for all users, or the user is authenticated but he/she is not granted access for this resource|

The error type SHOULD be chosen from this table and be accompanied by the specified HTTP status code. 
An example of a valid JSON error response is:

```json
"error": {
            "errorCode": 400,
            "errorMessage": "Missing mandatory parameter referenceName"
        }
```    




## <a name="beacon-api-example"></a>Beacon API Example
#### - /
Example of how to use the GET method in the "/" path:    

```bash
 curl -v http://localhost:5000/
```

```bash
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
```


#### - /query
Example of how to use the GET method in the "/query" path:
```bash
curl -v 'http://localhost:5000/query?referenceName=1&start=0&end=0&startMin=28000000&startMax=29000000&endMin=28000000&endMax=29000000&referenceBases=A&alternateBases=T&assemblyId=GRCh37&datasetIds=EGAD00000000028&includeDatasetResponses=ALL'
```

```bash
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
```
    

Example of how to use the POST method in the "/query" path:

```bash
curl -v -d "referenceName=1&start=14929&referenceBases=A&alternateBases=G&assemblyId=GRCh37&datasetIds=EGAD00000000028&includeDatsetResponses=ALL" http://localhost:5000/query
```

```bash
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

```

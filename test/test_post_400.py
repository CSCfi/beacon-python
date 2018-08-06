import requests

#URL = 'http://localhost:8080/'
#URL_query = 'http://localhost:8080/query'

URL = 'https://beaconapi-elixirbeacon.rahtiapp.fi/'
URL_query = 'https://beaconapi-elixirbeacon.rahtiapp.fi/query'


########################################## Missing parameter check #####################################################
def test_missing_refName():
    payload = {#'referenceName': '1',
               'start': 123,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00001000740',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'Missing mandatory parameter referenceName'

def test_missing_start_and_startMin():
    payload = {'referenceName': '1',
               #'start': 123,
               #'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00001000740',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'Missing mandatory parameter start or startMin'

def test_missing_refBases():
    payload = {'referenceName': '1',
               'start': 123,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               #'referenceBases': 'A',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00001000740',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'Missing mandatory parameter referenceBases'


def test_missing_altBases():
    payload = {'referenceName': '1',
               'start': 123,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               #'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00001000740',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'Missing mandatory parameter alternateBases or variantType'



def test_missing_assemblyId():
    payload = {'referenceName': '1',
               'start': 123,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'C',
               #'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00001000740',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'Missing mandatory parameter assemblyId'



########################################## Invalid parameter check #####################################################
def test_invalid_refName1():
    payload = {'referenceName': '99',
               'start': 123,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00000000028',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'referenceName not valid'


def test_invalid_refName2():
    payload = {'referenceName': 99,
               'start': 123,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00000000028',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'referenceName not valid'


def test_invalid_refName3():
    payload = {'referenceName': '0',
               'start': 123,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00000000028',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'Missing mandatory parameter referenceName'


def test_invalid_start1():
    payload = {'referenceName': '1',
               'start': 0,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00000000028',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'Missing mandatory parameter start or startMin'


def test_invalid_start2():
    payload = {'referenceName': '1',
               'start': -123,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00000000028',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'start not valid'


def test_invalid_refBases():
    payload = {'referenceName': '1',
               'start': 123,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'R',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00000000028',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'referenceBases not valid'


def test_invalid_altBases():
    payload = {'referenceName': '1',
               'start': 123,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'R',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00000000028',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'alternateBases not valid'


def test_invalid_assemblyId():
    payload = {'referenceName': '1',
               'start': 123,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'T',
               'assemblyId': '00000',
               'datasetIds': 'EGAD00000000028',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'assemblyId not valid'


def test_invalid_includeDatasetResponses():
    payload = {'referenceName': '1',
               'start': 123,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00000000028',
               'includeDatasetResponses': 'asd',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 400
    assert r.json()['message']['error']['errorMessage'] == 'includeDatasetResponses not valid'

########################################################################################################################

import requests

#URL = 'http://localhost:8080/'
#URL_query = 'http://localhost:8080/query'

URL = 'https://beaconapi-elixirbeacon.rahtiapp.fi/'
URL_query = 'https://beaconapi-elixirbeacon.rahtiapp.fi/query'

def test_false_get():
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
               'datasetIds': 'DATASET1',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.get(URL_query, params=payload, verify=False)
    assert r.status_code == 200
    assert r.json()['exists'] == False


def test_true1_get():
    payload = {'referenceName': '1',
               'start': 2947942,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'DATASET1',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.get(URL_query, params=payload, verify=False)
    assert r.status_code == 200
    assert r.json()['exists'] == True

def test_true2_get():
    payload = {'referenceName': '1',
               'start': 2985390,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'C',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'DATASET3',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.get(URL_query, params=payload, verify=False)
    assert r.status_code == 200
    assert r.json()['exists'] == True

def test_true3_get():
    payload = {'referenceName': '1',
               'start': 2985619,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'TG',
               'alternateBases': 'AGGCGGC',
               'assemblyId': 'GRCh37',
               'datasetIds': 'DATASET3',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.get(URL_query, params=payload, verify=False)
    assert r.status_code == 200
    assert r.json()['exists'] == True


def test_true4_get():
    payload = {'referenceName': '1',
               'start': 2986862,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'TG',
               'alternateBases': 'A',
               'assemblyId': 'GRCh37',
               'datasetIds': 'DATASET3',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.get(URL_query, params=payload, verify=False)
    assert r.status_code == 200
    assert r.json()['exists'] == True

#########################################  POST  ######################################################################


def test_false_post():
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
               'datasetIds': 'DATASET1',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 200
    assert r.json()['exists'] == False


def test_true1_post():
    payload = {'referenceName': '1',
               'start': 2947942,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'DATASET1',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 200
    assert r.json()['exists'] == True

def test_true2_post():
    payload = {'referenceName': '1',
               'start': 2985390,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'C',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'DATASET3',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 200
    assert r.json()['exists'] == True

def test_true3_post():
    payload = {'referenceName': '1',
               'start': 2985619,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'TG',
               'alternateBases': 'AGGCGGC',
               'assemblyId': 'GRCh37',
               'datasetIds': 'DATASET3',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 200
    assert r.json()['exists'] == True


def test_true4_post():
    payload = {'referenceName': '1',
               'start': 2986862,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'TG',
               'alternateBases': 'A',
               'assemblyId': 'GRCh37',
               'datasetIds': 'DATASET3',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 200
    assert r.json()['exists'] == True




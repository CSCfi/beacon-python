import requests


def test_false():
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
    r = requests.get('http://localhost:5000/query', params=payload)
    assert r.status_code == 200
    assert r.json()['exists'] == False


def test_true1():
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
    r = requests.get('http://localhost:5000/query', params=payload)
    assert r.status_code == 200
    assert r.json()['exists'] == True

def test_true2():
    payload = {'referenceName': '1',
               'start': 3055827,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'A',
               'alternateBases': 'T',
               'assemblyId': 'GRCh37',
               'datasetIds': 'DATASET2',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.get('http://localhost:5000/query', params=payload)
    assert r.status_code == 200
    assert r.json()['exists'] == True

def test_true3():
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
    r = requests.get('http://localhost:5000/query', params=payload)
    assert r.status_code == 200
    assert r.json()['exists'] == True




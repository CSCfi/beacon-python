import requests


def test_flase():
    payload = {'referenceName': '1',
               'start': '123',
               'startMin': '0',
               'startMax': '0',
               'end': '0',
               'endMin': '0',
               'endMax': '0',
               'referenceBases': 'A',
               'alternateBases': 'C',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00001000740',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.get('http://localhost:5000/query', params=payload)
    assert r.status_code == 200
    assert r.json()['exists'] == False


def test_true1():
    payload = {'referenceName': '1',
               'start': '14929',
               'startMin': '0',
               'startMax': '0',
               'end': '0',
               'endMin': '0',
               'endMax': '0',
               'referenceBases': 'A',
               'alternateBases': 'G',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00001000740',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.get('http://localhost:5000/query', params=payload)
    assert r.status_code == 200
    assert r.json()['exists'] == True

def test_true2():
    payload = {'referenceName': '1',
               'start': '0',
               'startMin': '28000000',
               'startMax': '29000000',
               'end': '0',
               'endMin': '28000000',
               'endMax': '29000000',
               'referenceBases': 'A',
               'alternateBases': 'G',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00001000740',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.get('http://localhost:5000/query', params=payload)
    assert r.status_code == 200
    assert r.json()['exists'] == True

def test_true3():
    payload = {'referenceName': '1',
               'start': '22332113',
               'startMin': '0',
               'startMax': '0',
               'end': '16913869',
               'endMin': '0',
               'endMax': '0',
               'referenceBases': 'TG',
               'alternateBases': 'T',
               'assemblyId': 'GRCh37',
               'datasetIds': 'EGAD00001000740',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.get('http://localhost:5000/query', params=payload)
    assert r.status_code == 200
    assert r.json()['exists'] == True




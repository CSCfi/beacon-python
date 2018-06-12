import requests


def test_post_200():
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
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post('http://localhost:5000/query', params=payload)
    assert r.status_code == 200
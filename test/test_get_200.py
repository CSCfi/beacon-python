import requests

URL = 'http://beaconapi-elixirbeacon.rahtiapp.fi/'
URL_query = 'http://beaconapi-elixirbeacon.rahtiapp.fi/query'

def test_get_response_code():
    r = requests.get(URL)
    assert r.status_code == 200

def test_get_200():
    payload = {'referenceName': '1',
               'start': 3216850,
               'startMin': 0,
               'startMax': 0,
               'end': 0,
               'endMin': 0,
               'endMax': 0,
               'referenceBases': 'G',
               'alternateBases': 'A',
               'assemblyId': 'GRCh37',
               'datasetIds': 'DATASET1',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.get(URL_query, params=payload)
    assert r.status_code == 200

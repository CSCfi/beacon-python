import requests

URL = 'http://beaconapi-elixirbeacon.rahtiapp.fi/'
URL_query = 'http://beaconapi-elixirbeacon.rahtiapp.fi/query'

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
               'datasetIds': 'DATASET3',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.post(URL_query, params=payload)
    assert r.status_code == 200
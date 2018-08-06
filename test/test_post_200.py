import requests

#URL = 'http://localhost:8080/'
#URL_query = 'http://localhost:8080/query'

URL = 'https://beaconapi-elixirbeacon.rahtiapp.fi/'
URL_query = 'https://beaconapi-elixirbeacon.rahtiapp.fi/query'

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
    r = requests.post(URL_query, params=payload, verify=False)
    assert r.status_code == 200
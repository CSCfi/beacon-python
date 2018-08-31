import requests

#RL = 'http://localhost:8080/'
#RL_query = 'http://localhost:8080/query'

URL = 'https://beaconapi-elixirbeacon.rahtiapp.fi/'
URL_query = 'https://beaconapi-elixirbeacon.rahtiapp.fi/query'

def test_unauthorized():
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
               'datasetIds': 'DATASET2',
               'includeDatasetResponses': 'ALL',
               }
    r = requests.get(URL_query, params=payload, verify=False)
    assert r.status_code == 401
    assert r.json()['message']['error']['errorMessage'] == 'User not authorized to access data set: DATASET2'

"""Integration tests.

The premises of the integration tests is to check that the endpoints ``info`` and ``query``
respond and have the loaded data.
"""

import aiohttp
import sys
import asyncio
import json
import logging

FORMAT = '[%(asctime)s][%(name)s][%(process)d %(processName)s][%(levelname)-8s] %(funcName)-8s: %(message)s'
logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


TESTS_NUMBER = 31
DATASET_IDS_LIST = ['urn:hg:1000genome', 'urn:hg:1000genome:registered',
                    'urn:hg:1000genome:controlled', 'urn:hg:1000genome:controlled1']

TOKEN = "eyJraWQiOiJyc2ExIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiJyZXF1ZXN0ZXJAZWxpeGlyL\
WV1cm9wZS5vcmciLCJwZXJtaXNzaW9uc19yZW1zIjpbeyJhZmZpbGlhdGlvbiI6IiIsImRhdGFzZXRzIj\
pbImRhdGFzZXQ6ZnJvbTphbm90aGVyOmJlYWNvbiIsInVybjpoZzoxMDAwZ2Vub21lOmNvbnRyb2xsZWQ\
iXSwic291cmNlX3NpZ25hdHVyZSI6IiIsInVybF9wcmVmaXgiOiIifV0sImlzcyI6Imh0dHA6Ly9zb21l\
Ym9keS5jb20iLCJleHAiOjk5OTk5OTk5OTk5LCJpYXQiOjE1NDc3OTQ2NTUsImp0aSI6IjZhZDdhYTQyL\
TNlOWMtNDgzMy1iZDE2LTc2NWNiODBjMjEwMiJ9.YQ50vcOKRNsyJrMKq7N-A4MtGxLilWVq0HDl4gUut\
FpbNMD4DEA8r4vqZpa08nL_5i01byD4_Y8G_AtJV9kEeW5Xu_19AELmDWnvyCi_ayAm46xcFcsUwcr7zo\
m-WIYtpkc8MP4aAlVAvHUjzxt5eHsQNpuJ4yo-dA3pB9VRsZo"

TOKEN_EMPTY = "eyJraWQiOiJyc2ExIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiJyZXF1ZXN0ZXJAZWx\
peGlyLWV1cm9wZS5vcmciLCJpc3MiOiJodHRwOi8vc29tZWJvZHkuY29tIiwiZXhwIjo5OTk5OTk5OTk5\
OSwiaWF0IjoxNTQ3Nzk0NjU1LCJqdGkiOiI2YWQ3YWE0Mi0zZTljLTQ4MzMtYmQxNi03NjVjYjgwYzIxM\
DIifQ.HPr3_N_4E-w_sIWS0kO7b-1VGVBuwQpgQoA2DRWj86YRt11JM_lpG58NrZwUOKXIOn4yV-HnrHe\
4pXn07bEZ_EgcqBsNnVHE51iiKZUS3v3gkBrLJ5miogjCdxz-wNnIm45ceSIW1PSRTkKDJpwmzigfvP_l\
GHpxwmUKAmRwFnw"


async def test_1():
    """Test the info endpoint.

    Info endpoint should respond with 4 datasets all in the list specified above.
    """
    LOG.debug(f'[01/{TESTS_NUMBER}] Test info endpoint')
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5050/') as resp:
            data = await resp.json()
            if 'datasets' in data and len(data['datasets']) > 0:
                for data_ids in data['datasets']:
                    # In info endpoint we get all dataset ids be them PUBLIC, REGISTERED or CONTROLLED
                    assert data_ids['id'] in DATASET_IDS_LIST, 'Dataset ID Error or not in list.'
            else:
                sys.exit('Info Endpoint Error!')


async def test_2():
    """Test query GET endpoint.

    Send a query with alternateBases. Expect data to be found (200).
    """
    LOG.debug(f'[02/{TESTS_NUMBER}] Test get query (normal query with alternateBases)')
    params = {'assemblyId': 'GRCh38', 'referenceName': 'MT',
              'start': 9, 'referenceBases': 'T', 'alternateBases': 'C',
              'includeDatasetResponses': 'HIT'}
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5050/query', params=params) as resp:
            data = await resp.json()
            if 'datasetAlleleResponses' in data and len(data['datasetAlleleResponses']) > 0:
                assert data['datasetAlleleResponses'][0]['datasetId'] == 'urn:hg:1000genome', 'DatasetID Error'
                assert data['datasetAlleleResponses'][0]['variantCount'] == 3, 'Variant count Error'
                assert data['datasetAlleleResponses'][0]['frequency'] == 0.00059195, 'frequency Error'
                assert data['datasetAlleleResponses'][0]['start'] == 9, 'Start coordinate Error'
                assert data['datasetAlleleResponses'][0]['end'] == 10, 'End coordinate Error'
                assert data['datasetAlleleResponses'][0]['exists'] is True, 'Inconsistent, exists is False, but all other pass'
            else:
                sys.exit('Query GET Endpoint Error!')


async def test_3():
    """Test query GET endpoint.

    Send a query with variantType. Expect data to be found (200).
    """
    LOG.debug(f'[03/{TESTS_NUMBER}] Test get query (normal query with variantType)')
    params = {'assemblyId': 'GRCh38', 'referenceName': 'MT',
              'start': 9, 'referenceBases': 'T', 'variantType': 'SNP',
              'includeDatasetResponses': 'HIT'}
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5050/query', params=params) as resp:
            data = await resp.json()
            if 'datasetAlleleResponses' in data and len(data['datasetAlleleResponses']) > 0:
                assert data['datasetAlleleResponses'][0]['datasetId'] == 'urn:hg:1000genome', 'DatasetID Error'
                assert data['datasetAlleleResponses'][0]['variantCount'] == 3, 'Variant count Error'
                assert data['datasetAlleleResponses'][0]['frequency'] == 0.00059195, 'frequency Error'
                assert data['datasetAlleleResponses'][0]['exists'] is True, 'Inconsistent, exists is False, but all other pass'
            else:
                sys.exit('Query GET Endpoint Error!')


async def test_4():
    """Test query GET endpoint.

    Send a query with missing required params. Expect a bad request (400).
    """
    LOG.debug(f'[04/{TESTS_NUMBER}] Test get query (missing params)')
    error_text = "Provided input: '{'assemblyId': 'GRCh38', 'start': 9, 'referenceBases': 'T', 'alternateBases': 'C', \
'includeDatasetResponses': 'HIT'}' does not seem correct because: ''referenceName' is a required property'"
    params = {'assemblyId': 'GRCh38',
              'start': 9, 'referenceBases': 'T', 'alternateBases': 'C',
              'includeDatasetResponses': 'HIT'}
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5050/query', params=params) as resp:
            data = await resp.json()

            if 'error' in data and len(data['error']) > 0:
                assert resp.status == 400, 'HTTP Status code error'
                assert data['error']['errorCode'] == 400, 'HTTP Status code error'
                assert data['error']['errorMessage'] == error_text
            else:
                sys.exit('Query GET Endpoint Error!')


async def test_5():
    """Test query GET endpoint.

    Send a query with wildcard alternateBases. Expect data to be found (200).
    """
    LOG.debug(f'[05/{TESTS_NUMBER}] Test get query (wildcards)')
    params = {'assemblyId': 'GRCh38', 'referenceName': 'MT',
              'start': 63, 'referenceBases': 'CT', 'alternateBases': 'NN',
              'includeDatasetResponses': 'HIT'}
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5050/query', params=params) as resp:
            data = await resp.json()
            if 'datasetAlleleResponses' in data and len(data['datasetAlleleResponses']) > 0:
                assert len(data['datasetAlleleResponses']) == 3, sys.exist('Should have three variants.')
                assert data['datasetAlleleResponses'][0]['datasetId'] == 'urn:hg:1000genome', 'DatasetID Error'
                assert data['datasetAlleleResponses'][0]['variantCount'] in [1, 118], 'Variant count Error'
                assert data['datasetAlleleResponses'][0]['frequency'] in [0.000197472, 0.023301737], 'frequency Error'
                assert data['datasetAlleleResponses'][0]['exists'] is True, 'Inconsistent, exists is False, but all other pass'
            else:
                sys.exit('Query GET Endpoint Error!')


async def test_6():
    """Test query POST endpoint.

    Send a query with alternateBases. Expect data to be found (200).
    """
    LOG.debug(f'[06/{TESTS_NUMBER}] Test post query (normal query with alternateBases)')
    payload = {"referenceName": "MT",
               "start": 9,
               "end": 10,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "includeDatasetResponses": "HIT"}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            if 'datasetAlleleResponses' in data and len(data['datasetAlleleResponses']) > 0:
                assert data['datasetAlleleResponses'][0]['datasetId'] == 'urn:hg:1000genome', 'DatasetID Error'
                assert data['datasetAlleleResponses'][0]['variantCount'] == 3, 'Variant count Error'
                assert data['datasetAlleleResponses'][0]['frequency'] == 0.00059195, 'frequency Error'
                assert data['datasetAlleleResponses'][0]['start'] == 9, 'Start coordinate Error'
                assert data['datasetAlleleResponses'][0]['end'] == 10, 'End coordinate Error'
                assert data['datasetAlleleResponses'][0]['exists'] is True, 'Inconsistent, exists is False, but all other pass'
            else:
                sys.exit('Query POST Endpoint Error!')


async def test_7():
    """Test query POST endpoint.

    Send a query with variantType. Expect data to be found (200).
    """
    LOG.debug(f'[07/{TESTS_NUMBER}] Test post query (normal query with variantType)')
    payload = {"referenceName": "MT",
               "start": 9,
               "end": 10,
               "referenceBases": "T",
               "variantType": "SNP",
               "assemblyId": "GRCh38",
               "includeDatasetResponses": "HIT"}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            if 'datasetAlleleResponses' in data and len(data['datasetAlleleResponses']) > 0:
                assert data['datasetAlleleResponses'][0]['datasetId'] == 'urn:hg:1000genome', 'DatasetID Error'
                assert data['datasetAlleleResponses'][0]['variantCount'] == 3, 'Variant count Error'
                assert data['datasetAlleleResponses'][0]['frequency'] == 0.00059195, 'frequency Error'
                assert data['datasetAlleleResponses'][0]['exists'] is True, 'Inconsistent, exists is False, but all other pass'
            else:
                sys.exit('Query POST Endpoint Error!')


async def test_8():
    """Test query POST endpoint.

    Send a query with missing required params. Expect a bad request (400).
    """
    LOG.debug(f'[08/{TESTS_NUMBER}] Test post query (missing params)')
    error_text = "Provided input: '{'start': 9, 'referenceBases': 'T', 'alternateBases': 'C', 'assemblyId': 'GRCh38', 'includeDatasetResponses': 'HIT'}' \
does not seem correct because: ''referenceName' is a required property'"
    payload = {"start": 9,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "includeDatasetResponses": "HIT"}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            if 'error' in data and len(data['error']) > 0:
                assert resp.status == 400, 'HTTP Status code error'
                assert data['error']['errorCode'] == 400, 'HTTP Status code error'
                assert data['error']['errorMessage'] == error_text
            else:
                sys.exit('Query POST Endpoint Error!')


async def test_9():
    """Test query GET endpoint.

    Send a query with wildcard alternateBases. Expect no data to be found exists=false, but query was good (200).
    """
    LOG.debug(f'[09/{TESTS_NUMBER}] Test get query (good query, empty response)')
    params = {'assemblyId': 'GRCh99', 'referenceName': 'MT',
              'start': 63, 'referenceBases': 'CT', 'alternateBases': 'NN',
              'includeDatasetResponses': 'HIT'}
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5050/query', params=params) as resp:
            data = await resp.json()
            assert data['exists'] is False, sys.exit('Query GET Endpoint Error!')


async def test_10():
    """Test query POST endpoint.

    Send a query targeted to a REGISTERED dataset without bona_fide_status. Expect failure (401).
    """
    LOG.debug(f'[10/{TESTS_NUMBER}] Test post query (fail to access registered data (no token))')
    payload = {"referenceName": "MT",
               "start": 9,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome:registered'],
               "includeDatasetResponses": "HIT"}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert 'WWW-Authenticate' in resp.headers, 'Missing WWW-Authenticate header'
            assert data['exists'] is None, sys.exit('Query POST Endpoint Error!')
            assert resp.status == 401, 'HTTP Status code error'


async def test_11():
    """Test query POST endpoint.

    Send a query targeted to a CONTROLLED dataset without token perms. Expect failure (401).
    """
    LOG.debug(f'[11/{TESTS_NUMBER}] Test post query (fail to access controlled data (no token))')
    payload = {"referenceName": "MT",
               "start": 9,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome:controlled'],
               "includeDatasetResponses": "HIT"}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert 'WWW-Authenticate' in resp.headers, 'Missing WWW-Authenticate header'
            assert data['exists'] is None, sys.exit('Query POST Endpoint Error!')
            assert resp.status == 401, 'HTTP Status code error'


async def test_12():
    """Test query POST endpoint.

    Send a multiquery targeting PUBLIC and CONTROLLED datasets without token perms. Expect only public data to be shown (200).
    """
    LOG.debug(f'[12/{TESTS_NUMBER}] Test post query (public data (success) and controlled data without token (failure))')
    payload = {"referenceName": "MT",
               "start": 9,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome', 'urn:hg:1000genome:controlled'],
               "includeDatasetResponses": "HIT"}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is True, sys.exit('Query POST Endpoint Error!')
            assert len(data['datasetAlleleResponses']) == 1, sys.exist('Should be able to retrieve only public.')


async def test_13():
    """Test query POST endpoint.

    Send a multiquery targeting PUBLIC and REGISTERED datasets with bona_fide_status. Expect data to be found (200).
    """
    LOG.debug(f'[13/{TESTS_NUMBER}] Test post query (public and registered with bona_fide_status)')
    payload = {"referenceName": "MT",
               "start": 9,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome', 'urn:hg:1000genome:registered'],
               "includeDatasetResponses": "HIT"}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is True, sys.exit('Query POST Endpoint Error!')
            assert len(data['datasetAlleleResponses']) == 2, sys.exist('Should be able to retrieve both requested.')


async def test_14():
    """Test query POST endpoint.

    Send a multiquery targeting REGISTERED and CONTROLLED datasets with bona_fide_status and token perms. Expect data to be found (200).
    """
    LOG.debug(f'[14/{TESTS_NUMBER}] Test post query (registered and controlled (bona fide + token perms))')
    payload = {"referenceName": "MT",
               "start": 9,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome:controlled', 'urn:hg:1000genome:registered'],
               "includeDatasetResponses": "HIT"}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is True, sys.exit('Query POST Endpoint Error!')
            assert len(data['datasetAlleleResponses']) == 2, sys.exist('Should be able to retrieve both requested.')


async def test_15():
    """Test query POST endpoint.

    Send a query targeting CONTROLLED dataset without token perms. Expect failure (403).
    """
    LOG.debug(f'[15/{TESTS_NUMBER}] Test post query (fail to access controlled data (token, but no perms))')
    payload = {"referenceName": "MT",
               "start": 9,
               "end": 10,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome:controlled'],
               "includeDatasetResponses": "HIT"}
    headers = {"Authorization": f"Bearer {TOKEN_EMPTY}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is None, sys.exit('Query POST Endpoint Error!')
            assert resp.status == 403, 'HTTP Status code error'


async def test_16():
    """Test query POST endpoint.

    Send a query targeting REGISTERED dataset with token, but no bona fide. Expect failure (403).
    """
    LOG.debug(f'[16/{TESTS_NUMBER}] Test post query (fail to access registered data (token, but no bona fide))')
    payload = {"referenceName": "MT",
               "start": 9,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome:registered'],
               "includeDatasetResponses": "HIT"}
    headers = {"Authorization": f"Bearer {TOKEN_EMPTY}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is None, sys.exit('Query POST Endpoint Error!')
            assert resp.status == 403, 'HTTP Status code error'


async def test_17():
    """Test query POST endpoint.

    Send a query targeting two CONTROLLED dataset with token perms, having access only to one of them. Expect data to be found (200).
    """
    LOG.debug(f'[17/{TESTS_NUMBER}] Test post query (request two controlled, having access to one)')
    payload = {"referenceName": "MT",
               "start": 9,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome:controlled', 'urn:hg:1000genome:controlled1'],
               "includeDatasetResponses": "HIT"}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is True, sys.exit('Query POST Endpoint Error!')
            assert len(data['datasetAlleleResponses']) == 1, sys.exist('Should be able to retrieve both requested.')


async def test_18():
    """Test query POST endpoint.

    Send a query with bad end parameter. Expect failure (400).
    """
    LOG.debug(f'[18/{TESTS_NUMBER}] Test post query (end < start)')
    payload = {"referenceName": "MT",
               "start": 9,
               "end": 8,
               "referenceBases": "T",
               "variantType": "SNP",
               "assemblyId": "GRCh38",
               "includeDatasetResponses": "HIT"}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is None, sys.exit('Query POST Endpoint Error!')
            assert resp.status == 400, 'HTTP Status code error'


async def test_19():
    """Test query POST endpoint.

    Send a query with bad start min/max parameters. Expect failure (400).
    """
    LOG.debug(f'[19/{TESTS_NUMBER}] Test post query (startMin > startMax)')
    payload = {"referenceName": "MT",
               "startMin": 21,
               "startMax": 20,
               "referenceBases": "T",
               "variantType": "SNP",
               "assemblyId": "GRCh38",
               "includeDatasetResponses": "HIT"}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is None, sys.exit('Query POST Endpoint Error!')
            assert resp.status == 400, 'HTTP Status code error'


async def test_20():
    """Test query POST endpoint.

    Send a query with bad end min/max parameters. Expect failure (400).
    """
    LOG.debug(f'[20/{TESTS_NUMBER}] Test post query (endMin > endMax)')
    payload = {"referenceName": "MT",
               "endMin": 21,
               "endMax": 20,
               "referenceBases": "T",
               "variantType": "SNP",
               "assemblyId": "GRCh38",
               "includeDatasetResponses": "HIT"}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is None, sys.exit('Query POST Endpoint Error!')
            assert resp.status == 400, 'HTTP Status code error'


async def test_21():
    """Test query POST endpoint.

    Send a query for non-existing variant targeting PUBLIC and CONTROLLED datasets with token perms, using MISS.
    Expect public and controlled data to be shown (200).
    """
    LOG.debug(f'[21/{TESTS_NUMBER}] Test Non-existing/MISS variant targeting PUBLIC and CONTROLLED datasets with token perms (expect all shown)')
    payload = {"referenceName": "MT",
               "start": 8,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome', 'urn:hg:1000genome:controlled'],
               "includeDatasetResponses": "MISS"}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is False, sys.exit('Query POST Endpoint Error!')
            assert len(data['datasetAlleleResponses']) == 2, sys.exit('Should be able to retrieve only public.')


async def test_22():
    """Test query POST endpoint.

    Send a query for non-existing variant targeting CONTROLLED datasets with token perms, using MISS.
    Expect the only the controlled, not the public data, to not be shown (200).
    """
    LOG.debug(f'[22/{TESTS_NUMBER}] Test non-existing variant targeting CONTROLLED datasets with token perms, using MISS (expect only controlled shown)')
    payload = {"referenceName": "MT",
               "start": 8,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome:controlled'],
               "includeDatasetResponses": "MISS"}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is False, sys.exit('Query POST Endpoint Error!')
            assert len(data['datasetAlleleResponses']) == 1, sys.exit('Should be able to retrieve only public.')


async def test_23():
    """Test query POST endpoint.

    Send a query for targeting a non-existing PUBLIC datasets, using ALL.
    Expect no data to be shown (200).
    """
    LOG.debug(f'[23/{TESTS_NUMBER}] Test query for targeting a non-existing PUBLIC datasets, using ALL. (expect no data shown)')
    payload = {"referenceName": "MT",
               "start": 9,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1111genome'],
               "includeDatasetResponses": "ALL"}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is False, sys.exit('Query POST Endpoint Error!')
            assert len(data['datasetAlleleResponses']) == 0, sys.exit('Should be able to retrieve only public.')


async def test_24():
    """Test query POST endpoint.

    Send a query for targeting one existing and one non-existing PUBLIC datasets, using ALL.
    Expect the existing PUBLIC data to be shown (200).
    """
    LOG.debug(f'[24/{TESTS_NUMBER}] Test query for targeting one existing and one non-existing PUBLIC datasets, using ALL. (expect only PUBLIC)')
    payload = {"referenceName": "MT",
               "start": 9,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1111genome', 'urn:hg:1000genome'],
               "includeDatasetResponses": "ALL"}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is True, sys.exit('Query POST Endpoint Error!')
            assert len(data['datasetAlleleResponses']) == 1, sys.exit('Should be able to retrieve only public.')


async def test_25():
    """Test query POST endpoint.

    Send a query for non-existing variant targeting three datasets, using ALL.
    Expect no hits, but data to be shown (200).
    """
    LOG.debug(f'[25/{TESTS_NUMBER}] Test query for targeting three datasets, using ALL. (expect data shown)')
    payload = {"referenceName": "MT",
               "start": 10,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome', 'urn:hg:1000genome:controlled', 'urn:hg:1000genome:registered'],
               "includeDatasetResponses": "ALL"}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is False, sys.exit('Query POST Endpoint Error!')
            assert len(data['datasetAlleleResponses']) == 3, sys.exit('Should be able to retrieve data for all datasets.')


async def test_26():
    """Test query POST endpoint.

    Send a query for non-existing variant targeting three datasets, using MISS.
    Expect no hits, but data to be shown (200).
    """
    LOG.debug(f'[26/{TESTS_NUMBER}] Test query for non-existing query targeting three datasets, using MISS. (expect data shown)')
    payload = {"referenceName": "MT",
               "start": 10,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome', 'urn:hg:1000genome:controlled', 'urn:hg:1000genome:registered'],
               "includeDatasetResponses": "MISS"}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is False, sys.exit('Query POST Endpoint Error!')
            assert len(data['datasetAlleleResponses']) == 3, sys.exit('Should be able to retrieve missing datasets.')


async def test_27():
    """Test query POST endpoint.

    Send a query targeting three datasets, using MISS.
    Expect hits, but no data to be shown (200).
    """
    LOG.debug(f'[27/{TESTS_NUMBER}] Test query for targeting three datasets, using MISS. (expect no data shown)')
    payload = {"referenceName": "MT",
               "start": 9,
               "referenceBases": "T",
               "alternateBases": "C",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome', 'urn:hg:1000genome:controlled', 'urn:hg:1000genome:registered'],
               "includeDatasetResponses": "MISS"}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is True, sys.exit('Query POST Endpoint Error!')
            assert len(data['datasetAlleleResponses']) == 0, sys.exit('Should not be able to retrieve any datasets.')


async def test_28():
    """Test query POST endpoint.

    Test BND query when end is smaller than start, with variantType and no mateName. Expect two hits, one for each direction (200).
    """
    LOG.debug(f'[28/{TESTS_NUMBER}] Test BND with variantType and no mateName query where end is smaller than start. Expect two hits.')
    payload = {"referenceName": "2",
               "start": 321681,
               "end": 123460,
               "referenceBases": "N",
               "assemblyId": "GRCh38",
               "variantType": "BND",
               "datasetIds": ['urn:hg:1000genome'],
               "includeDatasetResponses": "HIT"}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is True, sys.exit('Query POST Endpoint Error!')
            assert data['datasetAlleleResponses'][1]['mateStart'] == 123460, 'Mate start error'
            assert len(data['datasetAlleleResponses']) == 2, sys.exit('Should not be able to retrieve any datasets.')


async def test_29():
    """Test query POST endpoint.

    Test BND query with mateName and no variantType. Expect two hits, one for each direction (200).
    """
    LOG.debug(f'[29/{TESTS_NUMBER}] Test BND query with mateName and no variantType. Expect two hits.')
    payload = {"referenceName": "2",
               "mateName": "13",
               "start": 321681,
               "referenceBases": "N",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome'],
               "includeDatasetResponses": "HIT"}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is True, sys.exit('Query POST Endpoint Error!')
            assert data['datasetAlleleResponses'][0]['variantType'] == 'BND', 'Variant type error'
            assert len(data['datasetAlleleResponses']) == 2, sys.exit('Should not be able to retrieve any datasets.')


async def test_30():
    """Test query POST endpoint.

    Test mateName query without variantType, where end is smaller than start.
    Expect failure, because no variantType=BND and end is smaller than start (400).
    """
    LOG.debug(f'[30/{TESTS_NUMBER}] Test BND query where end is smaller than start with no variantType, expecting it to fail.')
    payload = {"referenceName": "2",
               "mateName": "13",
               "start": 321681,
               "end": 123460,
               "referenceBases": "N",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome'],
               "includeDatasetResponses": "HIT"}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is None, sys.exit('Query POST Endpoint Error!')
            assert resp.status == 400, 'HTTP Status code error'


async def test_31():
    """Test query POST endpoint.

    Test mateName query with startMin and startMax with no end params. Expect good query (200).
    """
    LOG.debug(f'[31/{TESTS_NUMBER}] Test mateName with start range and no end range.')
    payload = {"referenceName": "2",
               "mateName": "13",
               "startMin": 300000,
               "startMax": 400000,
               "referenceBases": "N",
               "assemblyId": "GRCh38",
               "datasetIds": ['urn:hg:1000genome'],
               "includeDatasetResponses": "HIT"}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5050/query', data=json.dumps(payload)) as resp:
            data = await resp.json()
            assert data['exists'] is True, sys.exit('Query POST Endpoint Error!')
            assert resp.status == 200, 'HTTP Status code error'


async def main():
    """Run the tests."""
    LOG.debug('Start integration tests')
    await test_1()
    await test_2()
    await test_3()
    await test_4()
    await test_5()
    await test_6()
    await test_7()
    await test_8()
    await test_9()
    await test_10()
    await test_11()
    await test_12()
    await test_13()
    await test_14()
    await test_15()
    await test_16()
    await test_17()
    # tests 18, 19 and 20 are also tested in the unit tests
    # redundant, but later we may want to valdiate against json schema
    await test_18()
    await test_19()
    await test_20()
    await test_21()
    await test_22()
    await test_23()
    await test_24()
    await test_25()
    await test_26()
    await test_27()
    await test_28()
    await test_29()
    await test_30()
    await test_31()
    LOG.debug('All integration tests have passed')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

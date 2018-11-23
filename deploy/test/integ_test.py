"""Integration tests.

The premises of the integration tests is to check that the endpoints ``info`` and ``query``
respond and have the loaded data.
"""

import aiohttp
import sys
import asyncio
import json


async def test_info():
    """Test the info endpoint."""
    print('[1/7] Test info endpoint')
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5050/') as resp:
            data = await resp.json()
            if 'datasets' in data and len(data['datasets']) > 0:
                assert data['datasets'][0]['id'] == 'urn:hg:1000genome', 'Dataset ID Error'
            else:
                sys.exit('Info Endpoint Error!')


async def test_get_query_1():
    """Test query GET endpoint."""
    print('[2/7] Test get query')
    params = {'assemblyId': 'GRCh38', 'referenceName': 'MT',
              'start': 10, 'referenceBases': 'T', 'alternateBases': 'C',
              'includeDatasetResponses': 'HIT'}
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5050/query', params=params) as resp:
            data = await resp.json()
            if 'datasetAlleleResponses' in data and len(data['datasetAlleleResponses']) > 0:
                assert data['datasetAlleleResponses'][0]['datasetId'] == 'urn:hg:1000genome', 'DatasetID Error'
                assert data['datasetAlleleResponses'][0]['variantCount'] == 3, 'Variant count Error'
                assert data['datasetAlleleResponses'][0]['frequency'] == 0.001183899, 'frequency Error'
                assert data['datasetAlleleResponses'][0]['exists'] is True, 'Inconsistent, exists is False, but all other pass'
            else:
                sys.exit('Query GET Endpoint Error!')


async def test_get_query_2():
    """Test query GET endpoint."""
    print('[3/7] Test get query')
    params = {'assemblyId': 'GRCh38', 'referenceName': 'MT',
              'start': 10, 'referenceBases': 'T', 'variantType': 'SNP',
              'includeDatasetResponses': 'HIT'}
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5050/query', params=params) as resp:
            data = await resp.json()
            if 'datasetAlleleResponses' in data and len(data['datasetAlleleResponses']) > 0:
                assert data['datasetAlleleResponses'][0]['datasetId'] == 'urn:hg:1000genome', 'DatasetID Error'
                assert data['datasetAlleleResponses'][0]['variantCount'] == 3, 'Variant count Error'
                assert data['datasetAlleleResponses'][0]['frequency'] == 0.001183899, 'frequency Error'
                assert data['datasetAlleleResponses'][0]['exists'] is True, 'Inconsistent, exists is False, but all other pass'
            else:
                sys.exit('Query GET Endpoint Error!')


async def test_get_query_3():
    """Test query GET endpoint."""
    print('[4/7] Test get query')
    params = {'assemblyId': 'GRCh38',
              'start': 10, 'referenceBases': 'T', 'alternateBases': 'C',
              'includeDatasetResponses': 'HIT'}
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5050/query', params=params) as resp:
            data = await resp.json()
            if 'error' in data and len(data['error']) > 0:
                assert resp.status == 400, 'HTTP Status code error'
                assert data['error']['errorCode'] == 400, 'HTTP Status code error'
                assert data['error']['errorMessage'] == "'referenceName' is a required property", 'Error message error'
            else:
                sys.exit('Query GET Endpoint Error!')


async def test_post_query_1():
    """Test query POST endpoint."""
    print('[5/7] Test post query')
    payload = {"referenceName": "MT",
               "start": 10,
               "startMax": 0,
               "end": 0,
               "endMin": 0,
               "endMax": 0,
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
                assert data['datasetAlleleResponses'][0]['frequency'] == 0.001183899, 'frequency Error'
                assert data['datasetAlleleResponses'][0]['exists'] is True, 'Inconsistent, exists is False, but all other pass'
            else:
                sys.exit('Query POST Endpoint Error!')


async def test_post_query_2():
    """Test query POST endpoint."""
    print('[6/7] Test post query')
    payload = {"referenceName": "MT",
               "start": 10,
               "startMax": 0,
               "end": 0,
               "endMin": 0,
               "endMax": 0,
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
                assert data['datasetAlleleResponses'][0]['frequency'] == 0.001183899, 'frequency Error'
                assert data['datasetAlleleResponses'][0]['exists'] is True, 'Inconsistent, exists is False, but all other pass'
            else:
                sys.exit('Query POST Endpoint Error!')


async def test_post_query_3():
    """Test query POST endpoint."""
    print('[7/7] Test post query')
    payload = {"start": 10,
               "startMax": 0,
               "end": 0,
               "endMin": 0,
               "endMax": 0,
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
                assert data['error']['errorMessage'] == "'referenceName' is a required property", 'Error message error'
            else:
                sys.exit('Query POST Endpoint Error!')


async def main():
    """Run the tests."""
    print('Start integration tests')
    await test_info()
    await test_get_query_1()
    await test_get_query_2()
    await test_get_query_3()
    await test_post_query_1()
    await test_post_query_2()
    await test_post_query_3()
    print('All integration tests have passed')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

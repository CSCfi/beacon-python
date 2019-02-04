"""Integration tests.

The premises of the integration tests is to check that the endpoints ``info`` and ``query``
respond and have the loaded data.
"""

import aiohttp
import sys
import asyncio
import json
import logging

FORMAT = '[%(asctime)s][%(name)s][%(process)d %(processName)s][%(levelname)-8s] %(funcName)s: %(message)s'
logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


TESTS_NUMBER = 9


async def test_1():
    """Test the info endpoint."""
    LOG.debug(f'[1/{TESTS_NUMBER}] Test info endpoint')
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5050/') as resp:
            data = await resp.json()
            if 'datasets' in data and len(data['datasets']) > 0:
                assert data['datasets'][0]['id'] == 'urn:hg:1000genome', 'Dataset ID Error'
            else:
                sys.exit('Info Endpoint Error!')


async def test_2():
    """Test query GET endpoint."""
    LOG.debug(f'[2/{TESTS_NUMBER}] Test get query')
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
                assert data['datasetAlleleResponses'][0]['exists'] is True, 'Inconsistent, exists is False, but all other pass'
            else:
                sys.exit('Query GET Endpoint Error!')


async def test_3():
    """Test query GET endpoint."""
    LOG.debug(f'[3/{TESTS_NUMBER}] Test get query')
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
    """Test query GET endpoint."""
    LOG.debug(f'[4/{TESTS_NUMBER}] Test get query')
    params = {'assemblyId': 'GRCh38',
              'start': 9, 'referenceBases': 'T', 'alternateBases': 'C',
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


async def test_5():
    """Test query GET endpoint."""
    LOG.debug(f'[5/{TESTS_NUMBER}] Test get query')
    params = {'assemblyId': 'GRCh38', 'referenceName': 'MT',
              'start': 63, 'referenceBases': 'CT', 'alternateBases': 'NN',
              'includeDatasetResponses': 'HIT'}
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5050/query', params=params) as resp:
            data = await resp.json()
            if 'datasetAlleleResponses' in data and len(data['datasetAlleleResponses']) > 0:
                assert data['datasetAlleleResponses'][0]['datasetId'] == 'urn:hg:1000genome', 'DatasetID Error'
                assert data['datasetAlleleResponses'][0]['variantCount'] == 1, 'Variant count Error'
                assert data['datasetAlleleResponses'][0]['frequency'] == 0.000197316, 'frequency Error'
                assert data['datasetAlleleResponses'][0]['exists'] is True, 'Inconsistent, exists is False, but all other pass'
            else:
                sys.exit('Query GET Endpoint Error!')


async def test_6():
    """Test query POST endpoint."""
    LOG.debug(f'[6/{TESTS_NUMBER}] Test post query')
    payload = {"referenceName": "MT",
               "start": 9,
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
                assert data['datasetAlleleResponses'][0]['frequency'] == 0.00059195, 'frequency Error'
                assert data['datasetAlleleResponses'][0]['exists'] is True, 'Inconsistent, exists is False, but all other pass'
            else:
                sys.exit('Query POST Endpoint Error!')


async def test_7():
    """Test query POST endpoint."""
    LOG.debug(f'[7/{TESTS_NUMBER}] Test post query')
    payload = {"referenceName": "MT",
               "start": 9,
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
                assert data['datasetAlleleResponses'][0]['frequency'] == 0.00059195, 'frequency Error'
                assert data['datasetAlleleResponses'][0]['exists'] is True, 'Inconsistent, exists is False, but all other pass'
            else:
                sys.exit('Query POST Endpoint Error!')


async def test_8():
    """Test query POST endpoint."""
    LOG.debug(f'[8/{TESTS_NUMBER}] Test post query')
    payload = {"start": 9,
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


async def test_9():
    """Test query GET endpoint."""
    LOG.debug(f'[9/{TESTS_NUMBER}] Test get query')
    params = {'assemblyId': 'GRCh99', 'referenceName': 'MT',
              'start': 63, 'referenceBases': 'CT', 'alternateBases': 'NN',
              'includeDatasetResponses': 'HIT'}
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5050/query', params=params) as resp:
            data = await resp.json()
            assert data['exists'] is False, sys.exit('Query GET Endpoint Error!')


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
    LOG.debug('All integration tests have passed')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

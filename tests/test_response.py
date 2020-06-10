from beacon_api.api.info import beacon_info, ga4gh_info
from beacon_api.api.query import query_request_handler
import asynctest
from beacon_api.schemas import load_schema
from beacon_api.utils.validate_jwt import get_key
from beacon_api.permissions.ga4gh import retrieve_user_data, get_jwk
import jsonschema
import json
import aiohttp
from aioresponses import aioresponses
from aiocache import caches


mock_dataset_metadata = {"id": "id1",
                         "name": "name",
                         "externalUrl": "url",
                         "description": "info",
                         "assemblyId": "GRCh38",
                         "variantCount": 0,
                         "callCount": 0,
                         "sampleCount": 2534,
                         "version": "v0.4",
                         "info": {"accessType": "PUBLIC"},
                         "createDateTime": "2013-05-02T12:00:00Z",
                         "updateDateTime": "2013-05-02T12:00:00Z"}

mock_controlled = ['id1'], ['id2'], []

mock_data = [{"datasetId": "id1",
              "referenceName": "MT",
              "externalUrl": "url",
              "note": "info",
              "variantCount": 3,
              "callCount": 2534,
              "sampleCount": 2534,
              "exists": True,
              "frequency": 0.001183899,
              "info": {"accessType": "PUBLIC"}},
             {"datasetId": "id2",
              "referenceName": "MT",
              "externalUrl": "url",
              "note": "info",
              "variantCount": 0,
              "callCount": 0,
              "sampleCount": 0,
              "exists": False,
              "frequency": 0,
              "info": {"accessType": "REGISTERED"}}]


class TestBasicFunctions(asynctest.TestCase):
    """Test supporting functions."""

    @asynctest.mock.patch('beacon_api.api.info.fetch_dataset_metadata')
    async def test_beacon_info(self, db_metadata):
        """Test info metadata response."""
        db_metadata.return_value = [mock_dataset_metadata]
        pool = asynctest.CoroutineMock()
        result = await beacon_info('localhost', pool)
        # if it is none no error occurred
        self.assertEqual(jsonschema.validate(json.loads(
            json.dumps(result)), load_schema('info')), None)
        db_metadata.assert_called()

    async def test_ga4gh_info(self):
        """Test info metadata response."""
        result = await ga4gh_info('localhost')
        # if it is none no error occurred
        self.assertEqual(jsonschema.validate(json.loads(
            json.dumps(result)), load_schema('service-info')), None)

    @asynctest.mock.patch('beacon_api.api.query.find_datasets')
    @asynctest.mock.patch('beacon_api.api.query.fetch_datasets_access')
    async def test_beacon_query(self, fetch_req_datasets, data_find):
        """Test query data response."""
        data_find.return_value = mock_data
        fetch_req_datasets.return_value = mock_controlled
        pool = asynctest.CoroutineMock()
        request = {"assemblyId": "GRCh38",
                   "referenceName": "MT",
                   "start": 0,
                   "referenceBases": "C",
                   "alternateBases": "T",
                   "includeDatasetResponses": "ALL",
                   "datasetIds": []}

        params = pool, 'POST', request, {'bona_fide_status': True, 'permissions': None}, "localhost"
        result = await query_request_handler(params)
        self.assertEqual(jsonschema.validate(json.loads(
            json.dumps(result)), load_schema('response')), None)
        data_find.assert_called()

    @asynctest.mock.patch('beacon_api.api.query.find_fusion')
    @asynctest.mock.patch('beacon_api.api.query.fetch_datasets_access')
    async def test_beacon_query_bnd(self, fetch_req_datasets, data_find):
        """Test query data response."""
        data_find.return_value = mock_data
        fetch_req_datasets.return_value = mock_controlled
        pool = asynctest.CoroutineMock()
        request = {"assemblyId": "GRCh38",
                   "referenceName": "MT",
                   "start": 0,
                   "referenceBases": "C",
                   "mateName": "1",
                   "includeDatasetResponses": "ALL",
                   "datasetIds": []}

        params = pool, 'POST', request, {'bona_fide_status': True, 'permissions': None}, "localhost"
        result = await query_request_handler(params)
        self.assertEqual(jsonschema.validate(json.loads(
            json.dumps(result)), load_schema('response')), None)
        data_find.assert_called()

    @aioresponses()
    async def test_bad_retrieve_user_data(self, m):
        """Test a failing userdata call because token is bad."""
        with self.assertRaises(aiohttp.web_exceptions.HTTPInternalServerError):
            await retrieve_user_data('bad_token')

    @aioresponses()
    async def test_bad_none_retrieve_user_data(self, m):
        """Test a failing userdata call because response didn't have ga4gh format."""
        m.get("http://test.csc.fi/userinfo", payload={"not_ga4gh": [{}]})
        user_data = await retrieve_user_data('good_token')
        self.assertEqual(user_data, None)

    @aioresponses()
    async def test_good_retrieve_user_data(self, m):
        """Test a passing call to retrieve user data."""
        m.get("http://test.csc.fi/userinfo", payload={"ga4gh_passport_v1": [{}]})
        user_data = await retrieve_user_data('good_token')
        self.assertEqual(user_data, [{}])

    @aioresponses()
    async def test_get_key(self, m):
        """Test retrieve get_key."""
        await caches.get('default').delete("jwk_key")
        data = {
            "keys": [
                {
                    "alg": "RS256",
                    "kty": "RSA",
                    "use": "sig",
                    "n": "yeNlzlub94YgerT030codqEztjfU_S6X4DbDA_iVKkjAWtYfPHDzz_sPCT1Axz6isZdf3lHpq_gYX4Sz-cbe4rjmigxUxr-FgKHQy3HeCdK6hNq9ASQvMK9LBOpXDNn\
7mei6RZWom4wo3CMvvsY1w8tjtfLb-yQwJPltHxShZq5-ihC9irpLI9xEBTgG12q5lGIFPhTl_7inA1PFK97LuSLnTJzW0bj096v_TMDg7pOWm_zHtF53qbVsI0e3v5nmdKXdF\
f9BjIARRfVrbxVxiZHjU6zL6jY5QJdh1QCmENoejj_ytspMmGW7yMRxzUqgxcAqOBpVm0b-_mW3HoBdjQ",
                    "e": "AQAB"
                }
            ]}
        m.get("http://test.csc.fi/jwk", payload=data)
        result = await get_key()
        # key = load_pem_public_key(result.encode('utf-8'), backend=default_backend())
        self.assertTrue(isinstance(result, dict))
        self.assertTrue(result["keys"][0]['alg'], 'RSA256')

    @aioresponses()
    async def test_get_jwk(self, m):
        """Test get JWK."""
        data = {
            "keys": [
                {
                    "alg": "RS256",
                    "kty": "RSA",
                    "use": "sig",
                    "n": "public_key",
                    "e": "AQAB"
                }
            ]}
        m.get("http://test.csc.fi/jwk", payload=data)
        result = await get_jwk('http://test.csc.fi/jwk')
        self.assertTrue(isinstance(result, dict))
        self.assertTrue(result["keys"][0]['alg'], 'RSA256')

    @asynctest.mock.patch('beacon_api.permissions.ga4gh.LOG')
    async def test_get_jwk_bad(self, mock_log):
        """Test get JWK exception log."""
        await get_jwk('http://test.csc.fi/jwk')
        mock_log.error.assert_called_with("Could not retrieve JWK from http://test.csc.fi/jwk")

    @asynctest.mock.patch('beacon_api.utils.validate_jwt.OAUTH2_CONFIG', return_value={'server': None})
    async def test_bad_get_key(self, oauth_none):
        """Test bad test_get_key."""
        with self.assertRaises(aiohttp.web_exceptions.HTTPInternalServerError):
            await get_key()

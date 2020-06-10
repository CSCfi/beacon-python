import asynctest
import aiohttp
from beacon_api.utils.db_load import parse_arguments, init_beacon_db, main
from beacon_api.conf.config import init_db_pool
from beacon_api.api.query import access_resolution
from beacon_api.utils.validate_jwt import token_scheme_check, verify_aud_claim
from beacon_api.permissions.ga4gh import get_ga4gh_controlled, get_ga4gh_bona_fide, validate_passport
from beacon_api.permissions.ga4gh import check_ga4gh_token, decode_passport, get_ga4gh_permissions
from .test_app import PARAMS, generate_token
from testfixtures import TempDirectory
from test.support import EnvironmentVarGuard


def mock_token(bona_fide, permissions, auth):
    """Mock a processed token."""
    return {"bona_fide_status": bona_fide,
            "permissions": permissions,
            "authenticated": auth}


class MockDecodedPassport:
    """Mock JWT."""

    def __init__(self, validated=True):
        """Initialise mock JWT."""
        self.validated = validated

    def validate(self):
        """Invoke validate."""
        if self.validated:
            return True
        else:
            raise Exception


class MockBeaconDB:
    """BeaconDB mock.

    We test this in db_load.
    """

    def __init__(self):
        """Initialize class."""
        pass

    async def connection(self):
        """Mimic connection."""
        pass

    async def close(self):
        """Mimic connection."""
        pass

    async def check_tables(self, array):
        """Mimic check_tables."""
        return ['DATASET1', 'DATASET2']

    async def create_tables(self, sql_file):
        """Mimic create_tables."""
        pass

    async def insert_variants(self, dataset_id, variants, len_samples):
        """Mimic insert_variants."""
        pass

    async def load_metadata(self, vcf, metafile, datafile):
        """Mimic load_metadata."""
        pass

    async def load_datafile(self, vcf, datafile, datasetId):
        """Mimic load_datafile."""
        return ["datasetId", "variants"]


class TestBasicFunctions(asynctest.TestCase):
    """Test supporting functions."""

    def setUp(self):
        """Initialise BeaconDB object."""
        self._dir = TempDirectory()

    def tearDown(self):
        """Close database connection after tests."""
        self._dir.cleanup_all()

    def test_parser(self):
        """Test argument parsing."""
        parsed = parse_arguments(['/path/to/datafile.csv', '/path/to/metadata.json'])
        self.assertEqual(parsed.datafile, '/path/to/datafile.csv')
        self.assertEqual(parsed.metadata, '/path/to/metadata.json')

    @asynctest.mock.patch('beacon_api.conf.config.asyncpg')
    async def test_init_pool(self, db_mock):
        """Test database connection pool creation."""
        db_mock.return_value = asynctest.CoroutineMock(name='create_pool')
        db_mock.create_pool = asynctest.CoroutineMock()
        await init_db_pool()
        db_mock.create_pool.assert_called()

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.BeaconDB')
    @asynctest.mock.patch('beacon_api.utils.db_load.VCF')
    async def test_init_beacon_db(self, mock_vcf, db_mock, mock_log):
        """Test beacon_init db call."""
        db_mock.return_value = MockBeaconDB()
        metadata = """{"name": "DATASET1",
                    "description": "example dataset number 1",
                    "assemblyId": "GRCh38",
                    "version": "v1",
                    "sampleCount": 2504,
                    "externalUrl": "https://datasethost.org/dataset1",
                    "accessType": "PUBLIC"}"""
        metafile = self._dir.write('data.json', metadata.encode('utf-8'))
        data = """MOCK VCF file"""
        datafile = self._dir.write('data.vcf', data.encode('utf-8'))
        await init_beacon_db([datafile, metafile])
        mock_log.info.mock_calls = ['Mark the database connection to be closed',
                                    'The database connection has been closed']

    @asynctest.mock.patch('beacon_api.utils.db_load.init_beacon_db')
    def test_main_db(self, mock_init):
        """Test run asyncio main beacon init."""
        main()
        mock_init.assert_called()

    def test_aud_claim(self):
        """Test aud claim function."""
        env = EnvironmentVarGuard()
        env.set('JWT_AUD', "aud1,aud2")
        result = verify_aud_claim()
        # Because it is false we expect it not to be parsed
        expected = (False, [])
        self.assertEqual(result, expected)
        env.unset('JWT_AUD')

    def test_token_scheme_check_bad(self):
        """Test token scheme no token."""
        # This might never happen, yet lets prepare for it
        with self.assertRaises(aiohttp.web_exceptions.HTTPUnauthorized):
            token_scheme_check("", 'https', {}, 'localhost')

    def test_access_resolution_base(self):
        """Test assumptions for access resolution.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [], False)
        host = 'localhost'
        result = access_resolution(request, token, host, ["1", "2"], ["3", "4"], ["5", "6"])
        self.assertListEqual(result[0], ['PUBLIC'])
        intermediate_list = result[1]
        intermediate_list.sort()
        self.assertListEqual(["1", "2"], intermediate_list)

    def test_access_resolution_no_controlled(self):
        """Test assumptions for access resolution for token but no controlled datasets.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [], True)
        host = 'localhost'
        result = access_resolution(request, token, host, ["1", "2"], ["3", "4"], ["5", "6"])
        self.assertListEqual(result[0], ['PUBLIC'])
        intermediate_list = result[1]
        intermediate_list.sort()
        self.assertListEqual(["1", "2"], intermediate_list)

    def test_access_resolution_registered(self):
        """Test assumptions for access resolution for token with just bona_fide.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(True, [], True)
        host = 'localhost'
        result = access_resolution(request, token, host, ["1", "2"], ["3", "4"], ["5", "6"])
        self.assertListEqual(result[0], ['PUBLIC', 'REGISTERED'])
        intermediate_list = result[1]
        intermediate_list.sort()
        self.assertListEqual(["1", "2", "3", "4"], intermediate_list)

    def test_access_resolution_controlled_no_registered(self):
        """Test assumptions for access resolution for token and no bona_fide.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, ["5", "6"], True)
        host = 'localhost'
        result = access_resolution(request, token, host, ["1", "2"], ["3", "4"], ["5", "6"])
        self.assertListEqual(result[0], ['PUBLIC', 'CONTROLLED'])
        intermediate_list = result[1]
        intermediate_list.sort()
        self.assertListEqual(["1", "2", "5", "6"], intermediate_list)

    def test_access_resolution_controlled_registered(self):
        """Test assumptions for access resolution for token and bona_fide.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(True, ["5", "6"], True)
        host = 'localhost'
        result = access_resolution(request, token, host, ["1", "2"], ["3", "4"], ["5", "6"])
        self.assertListEqual(result[0], ['PUBLIC', 'REGISTERED' ,'CONTROLLED'])
        intermediate_list = result[1]
        intermediate_list.sort()
        self.assertListEqual(["1", "2", "3", "4", "5", "6"], intermediate_list)

    def test_access_resolution_bad_registered(self):
        """Test assumptions for access resolution for requested registered Unauthorized.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [], False)
        host = 'localhost'
        with self.assertRaises(aiohttp.web_exceptions.HTTPUnauthorized):
            access_resolution(request, token, host, [], ["3"], [])

    def test_access_resolution_no_registered2(self):
        """Test assumptions for access resolution for requested registered Forbidden.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [], True)
        host = 'localhost'
        with self.assertRaises(aiohttp.web_exceptions.HTTPForbidden):
            access_resolution(request, token, host, [], ["4"], [])

    def test_access_resolution_controlled_forbidden(self):
        """Test assumptions for access resolution for requested controlled Forbidden.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [7], True)
        host = 'localhost'
        with self.assertRaises(aiohttp.web_exceptions.HTTPForbidden):
            access_resolution(request, token, host, [], ["6"], [])

    def test_access_resolution_controlled_unauthorized(self):
        """Test assumptions for access resolution for requested controlled Unauthorized.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [], False)
        host = 'localhost'
        with self.assertRaises(aiohttp.web_exceptions.HTTPUnauthorized):
            access_resolution(request, token, host, [], ["5"], [])

    def test_access_resolution_controlled_no_perms(self):
        """Test assumptions for access resolution for requested controlled Forbidden.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, ["7"], True)
        host = 'localhost'
        result = access_resolution(request, token, host, ["2"], ["6"], [])
        self.assertEqual(result, (['PUBLIC'], ["2"]))

    def test_access_resolution_controlled_some(self):
        """Test assumptions for access resolution for requested controlled some datasets.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, ["5"], True)
        host = 'localhost'
        result = access_resolution(request, token, host, [], [], ["5", "6"])
        self.assertEqual(result, (['CONTROLLED'], ["5"]))

    def test_access_resolution_controlled_no_perms_public(self):
        """Test assumptions for access resolution for requested controlled and public, returning public only.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [], False)
        host = 'localhost'
        result = access_resolution(request, token, host, ["1"], [], ["5"])
        self.assertEqual(result, (['PUBLIC'], ["1"]))

    def test_access_resolution_controlled_no_perms_bonafide(self):
        """Test assumptions for access resolution for requested controlled and registered, returning registered only.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(True, [], True)
        host = 'localhost'
        result = access_resolution(request, token, host, [], ["4"], ["7"])
        self.assertEqual(result, (['REGISTERED'], ["4"]))

    def test_access_resolution_controlled_never_reached(self):
        """Test assumptions for access resolution for requested controlled unauthorized.

        By default permissions cannot be None, at worst empty set, thus this might never be reached.
        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, None, False)
        host = 'localhost'
        with self.assertRaises(aiohttp.web_exceptions.HTTPUnauthorized):
            access_resolution(request, token, host, [], [], ["8"])

    def test_access_resolution_controlled_never_reached2(self):
        """Test assumptions for access resolution for requested controlled forbidden.

        By default permissions cannot be None, at worst empty set, thus this might never be reached.
        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, None, True)
        host = 'localhost'
        with self.assertRaises(aiohttp.web_exceptions.HTTPForbidden):
            access_resolution(request, token, host, [], [], ["8"])

    @asynctest.mock.patch('beacon_api.permissions.ga4gh.validate_passport')
    async def test_ga4gh_controlled(self, m_validation):
        """Test ga4gh permissions claim parsing."""
        # Test: no passports, no permissions
        datasets = await get_ga4gh_controlled([])
        self.assertEqual(datasets, set())
        # Test: 1 passport, 1 unique dataset, 1 permission
        passport = {"ga4gh_visa_v1": {"type": "ControlledAccessGrants",
                                      "value": "https://institution.org/EGAD01",
                                      "source": "https://ga4gh.org/duri/no_org",
                                      "by": "self",
                                      "asserted": 1539069213,
                                      "expires": 4694742813}}
        m_validation.return_value = passport
        dataset = await get_ga4gh_controlled([{}])  # one passport
        self.assertEqual(dataset, {'EGAD01'})
        # Test: 2 passports, 1 unique dataset, 1 permission (permissions must not be duplicated)
        passport = {"ga4gh_visa_v1": {"type": "ControlledAccessGrants",
                                      "value": "https://institution.org/EGAD01",
                                      "source": "https://ga4gh.org/duri/no_org",
                                      "by": "self",
                                      "asserted": 1539069213,
                                      "expires": 4694742813}}
        m_validation.return_value = passport
        dataset = await get_ga4gh_controlled([{}, {}])  # two passports
        self.assertEqual(dataset, {'EGAD01'})
        # Test: 2 passports, 2 unique datasets, 2 permissions
        # Can't test this case with the current design!
        # Would need a way for validate_passport() to mock two different results

    async def test_ga4gh_bona_fide(self):
        """Test ga4gh statuses claim parsing."""
        passports = [("enc", "header", {
                     "ga4gh_visa_v1": {"type": "AcceptedTermsAndPolicies",
                                       "value": "https://doi.org/10.1038/s41431-018-0219-y",
                                       "source": "https://ga4gh.org/duri/no_org",
                                       "by": "self",
                                       "asserted": 1539069213,
                                       "expires": 4694742813}
                     }),
                     ("enc", "header", {
                      "ga4gh_visa_v1": {"type": "ResearcherStatus",
                                        "value": "https://doi.org/10.1038/s41431-018-0219-y",
                                        "source": "https://ga4gh.org/duri/no_org",
                                        "by": "peer",
                                        "asserted": 1539017776,
                                        "expires": 1593165413}})]
        # Good test: both required passport types contained the correct value
        bona_fide_status = await get_ga4gh_bona_fide(passports)
        self.assertEqual(bona_fide_status, True)  # has bona fide
        # Bad test: missing passports of required type
        passports_empty = []
        bona_fide_status = await get_ga4gh_bona_fide(passports_empty)
        self.assertEqual(bona_fide_status, False)  # doesn't have bona fide

    @asynctest.mock.patch('beacon_api.permissions.ga4gh.get_jwk')
    @asynctest.mock.patch('beacon_api.permissions.ga4gh.jwt')
    @asynctest.mock.patch('beacon_api.permissions.ga4gh.LOG')
    async def test_validate_passport(self, mock_log, m_jwt, m_jwk):
        """Test passport validation."""
        m_jwk.return_value = 'jwk'
        # Test: validation passed
        m_jwt.return_value = MockDecodedPassport()
        await validate_passport({})

        # # Test: validation failed
        m_jwt.return_value = MockDecodedPassport(validated=False)
        # with self.assertRaises(Exception):
        await validate_passport({})
        # we are not raising the exception we are just doing a log
        # need to assert the log called
        mock_log.error.assert_called_with("Something went wrong when processing JWT tokens: 1")

    @asynctest.mock.patch('beacon_api.permissions.ga4gh.get_ga4gh_permissions')
    async def test_check_ga4gh_token(self, m_get_perms):
        """Test token scopes."""
        # Test: no scope found
        decoded_data = {}
        dataset_permissions, bona_fide_status = await check_ga4gh_token(decoded_data, {}, False, set())
        self.assertEqual(dataset_permissions, set())
        self.assertEqual(bona_fide_status, False)
        # Test: scope is ok, but no claims
        decoded_data = {'scope': ''}
        dataset_permissions, bona_fide_status = await check_ga4gh_token(decoded_data, {}, False, set())
        self.assertEqual(dataset_permissions, set())
        self.assertEqual(bona_fide_status, False)
        # Test: scope is ok, claims are ok
        m_get_perms.return_value = {'EGAD01'}, True
        decoded_data = {'scope': 'openid ga4gh_passport_v1'}
        dataset_permissions, bona_fide_status = await check_ga4gh_token(decoded_data, {}, False, set())
        self.assertEqual(dataset_permissions, {'EGAD01'})
        self.assertEqual(bona_fide_status, True)

    async def test_decode_passport(self):
        """Test key-less JWT decoding."""
        token, _ = generate_token('http://test.csc.fi')
        header, payload = await decode_passport(token)
        self.assertEqual(header.get('alg'), 'HS256')
        self.assertEqual(payload.get('iss'), 'http://test.csc.fi')

    @asynctest.mock.patch('beacon_api.permissions.ga4gh.get_ga4gh_bona_fide')
    @asynctest.mock.patch('beacon_api.permissions.ga4gh.get_ga4gh_controlled')
    @asynctest.mock.patch('beacon_api.permissions.ga4gh.decode_passport')
    @asynctest.mock.patch('beacon_api.permissions.ga4gh.retrieve_user_data')
    async def test_get_ga4gh_permissions(self, m_userinfo, m_decode, m_controlled, m_bonafide):
        """Test GA4GH permissions main function."""
        # Test: no data (nothing)
        m_userinfo.return_value = [{}]
        header = {}
        payload = {}
        m_decode.return_value = header, payload
        m_controlled.return_value = set()
        m_bonafide.return_value = False
        dataset_permissions, bona_fide_status = await get_ga4gh_permissions('token')
        self.assertEqual(dataset_permissions, set())
        self.assertEqual(bona_fide_status, False)
        # Test: permissions
        m_userinfo.return_value = [{}]
        header = {}
        payload = {
            'ga4gh_visa_v1': {
                'type': 'ControlledAccessGrants'
            }
        }
        m_decode.return_value = header, payload
        m_controlled.return_value = {'EGAD01'}
        m_bonafide.return_value = False
        dataset_permissions, bona_fide_status = await get_ga4gh_permissions('token')
        self.assertEqual(dataset_permissions, {'EGAD01'})
        self.assertEqual(bona_fide_status, False)
        # Test: bona fide
        m_userinfo.return_value = [{}]
        header = {}
        payload = {
            'ga4gh_visa_v1': {
                'type': 'ResearcherStatus'
            }
        }
        m_decode.return_value = header, payload
        m_controlled.return_value = set()
        m_bonafide.return_value = True
        dataset_permissions, bona_fide_status = await get_ga4gh_permissions('token')
        self.assertEqual(dataset_permissions, set())
        self.assertEqual(bona_fide_status, True)


if __name__ == '__main__':
    asynctest.main()

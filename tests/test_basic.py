import asynctest
import aiohttp
from beacon_api.utils.db_load import parse_arguments, init_beacon_db, main
from beacon_api.conf.config import init_db_pool
from beacon_api.api.query import access_resolution
from beacon_api.permissions.rems import get_rems_controlled
from beacon_api.permissions.ga4gh import get_ga4gh_controlled
from .test_app import PARAMS
from testfixtures import TempDirectory


def mock_token(bona_fide, permissions, auth):
    """Mock a processed token."""
    return {"bona_fide_status": bona_fide,
            "permissions": permissions,
            "authenticated": auth}


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

    def test_access_resolution_base(self):
        """Test assumptions for access resolution.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [], False)
        host = 'localhost'
        result = access_resolution(request, token, host, [1, 2], [3, 4], [5, 6])
        assert result == (['PUBLIC'], [1, 2])

    def test_access_resolution_no_controlled(self):
        """Test assumptions for access resolution for token but no controlled datasets.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [], True)
        host = 'localhost'
        result = access_resolution(request, token, host, [1, 2], [3, 4], [5, 6])
        assert result == (['PUBLIC'], [1, 2])

    def test_access_resolution_registered(self):
        """Test assumptions for access resolution for token with just bona_fide.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(True, [], True)
        host = 'localhost'
        result = access_resolution(request, token, host, [1, 2], [3, 4], [5, 6])
        assert result == (['PUBLIC', 'REGISTERED'], [1, 2, 3, 4])

    def test_access_resolution_controlled_no_registered(self):
        """Test assumptions for access resolution for token and no bona_fide.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [5, 6], True)
        host = 'localhost'
        result = access_resolution(request, token, host, [1, 2], [3, 4], [5, 6])
        assert result == (['PUBLIC', 'CONTROLLED'], [1, 2, 5, 6])

    def test_access_resolution_controlled_registered(self):
        """Test assumptions for access resolution for token and bona_fide.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(True, [5, 6], True)
        host = 'localhost'
        result = access_resolution(request, token, host, [1, 2], [3, 4], [5, 6])
        assert result == (['PUBLIC', 'REGISTERED', 'CONTROLLED'], [1, 2, 3, 4, 5, 6])

    def test_access_resolution_bad_registered(self):
        """Test assumptions for access resolution for requested registered Unauthorized.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [], False)
        host = 'localhost'
        with self.assertRaises(aiohttp.web_exceptions.HTTPUnauthorized):
            access_resolution(request, token, host, [], [3], [])

    def test_access_resolution_no_registered2(self):
        """Test assumptions for access resolution for requested registered Forbidden.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [], True)
        host = 'localhost'
        with self.assertRaises(aiohttp.web_exceptions.HTTPForbidden):
            access_resolution(request, token, host, [], [4], [])

    def test_access_resolution_controlled_forbidden(self):
        """Test assumptions for access resolution for requested controlled Forbidden.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [7], True)
        host = 'localhost'
        with self.assertRaises(aiohttp.web_exceptions.HTTPForbidden):
            access_resolution(request, token, host, [], [6], [])

    def test_access_resolution_controlled_unauthorized(self):
        """Test assumptions for access resolution for requested controlled Unauthorized.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [], False)
        host = 'localhost'
        with self.assertRaises(aiohttp.web_exceptions.HTTPUnauthorized):
            access_resolution(request, token, host, [], [5], [])

    def test_access_resolution_controlled_no_perms(self):
        """Test assumptions for access resolution for requested controlled Forbidden.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [7], True)
        host = 'localhost'
        result = access_resolution(request, token, host, [2], [6], [])
        assert result == (['PUBLIC'], [2])

    def test_access_resolution_controlled_some(self):
        """Test assumptions for access resolution for requested controlled some datasets.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [5], True)
        host = 'localhost'
        result = access_resolution(request, token, host, [], [], [5, 6])
        assert result == (['CONTROLLED'], [5])

    def test_access_resolution_controlled_no_perms_public(self):
        """Test assumptions for access resolution for requested controlled and public, returning public only.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, [], False)
        host = 'localhost'
        result = access_resolution(request, token, host, [1], [], [5])
        assert result == (['PUBLIC'], [1])

    def test_access_resolution_controlled_no_perms_bonafide(self):
        """Test assumptions for access resolution for requested controlled and registered, returning registered only.

        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(True, [], True)
        host = 'localhost'
        result = access_resolution(request, token, host, [], [4], [7])
        assert result == (['REGISTERED'], [4])

    def test_access_resolution_controlled_never_reached(self):
        """Test assumptions for access resolution for requested controlled unauthorized.

        By default permissions cannot be None, at worst empty set, thus this might never be reached.
        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, None, False)
        host = 'localhost'
        with self.assertRaises(aiohttp.web_exceptions.HTTPUnauthorized):
            access_resolution(request, token, host, [], [], [8])

    def test_access_resolution_controlled_never_reached2(self):
        """Test assumptions for access resolution for requested controlled forbidden.

        By default permissions cannot be None, at worst empty set, thus this might never be reached.
        It is based on the result of fetch_datasets_access function.
        """
        request = PARAMS
        token = mock_token(False, None, True)
        host = 'localhost'
        with self.assertRaises(aiohttp.web_exceptions.HTTPForbidden):
            access_resolution(request, token, host, [], [], [8])

    def test_rems_controlled(self):
        """Test rems permissions claim parsing."""
        claim = [{"affiliation": "",
                  "datasets": ["EGAD01", "urn:hg:example-controlled"],
                  "source_signature": "",
                  "url_prefix": ""},
                 {"affiliation": "",
                  "datasets": ["urn:hg:example-controlled", "EGAD02",
                               "urn:hg:example-controlled3"],
                  "source_signature": "",
                  "url_prefix": ""}]
        self.assertCountEqual(get_rems_controlled(claim),
                              ['EGAD01', 'urn:hg:example-controlled',
                               'urn:hg:example-controlled3', 'EGAD02'])

    @asynctest.mock.patch('beacon_api.permissions.ga4gh.retrieve_dataset_permissions')
    async def test_ga4gh_controlled(self, userinfo):
        """Test ga4gh permissions claim parsing."""
        userinfo.return_value = {
            "ControlledAccessGrants": [
                {
                    "value": "https://www.ebi.ac.uk/ega/EGAD000000000001",
                    "source": "https://ega-archive.org/dacs/EGAC00000000001",
                    "by": "dac",
                    "authoriser": "john.doe@dac.org",
                    "asserted": 1546300800,
                    "expires": 1577836800
                },
                {
                    "value": "https://www.ebi.ac.uk/ega/EGAD000000000002",
                    "source": "https://ega-archive.org/dacs/EGAC00000000001",
                    "by": "dac",
                    "authoriser": "john.doe@dac.org",
                    "asserted": 1546300800,
                    "expires": 1577836800
                },
                {
                    "value": "no-prefix-dataset",
                    "source": "https://ega-archive.org/dacs/EGAC00000000001",
                    "by": "dac",
                    "authoriser": "john.doe@dac.org",
                    "asserted": 1546300800,
                    "expires": 1577836800
                }
            ]
        }
        token_claim = ["ga4gh.ControlledAccessGrants"]
        token = 'this_is_a_jwt'
        datasets = await get_ga4gh_controlled(token, token_claim)
        self.assertEqual(datasets, {'EGAD000000000001', 'EGAD000000000002', 'no-prefix-dataset'})


if __name__ == '__main__':
    asynctest.main()

import asynctest
from beacon_api.utils.db_load import parse_arguments, init_beacon_db, main
from beacon_api.conf.config import init_db_pool
from beacon_api.permissions.rems import get_rems_controlled
from testfixtures import TempDirectory


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


if __name__ == '__main__':
    asynctest.main()

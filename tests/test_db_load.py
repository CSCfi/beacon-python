import unittest
import asynctest
from testfixtures import TempDirectory
from beacon_api.utils.db_load import BeaconDB


class Transaction:
    """Class Connection."""

    def __init__(self, *args, **kwargs):
        """Initialize class."""
        pass

    async def __aenter__(self):
        """Initialize class."""
        pass

    async def __aexit__(self, *args):
        """Initialize class."""
        pass


class Connection:
    """Class Connection."""

    def __init__(self):
        """Initialize class."""
        pass

    async def fetch(self, query):
        """Mimic fetch."""
        return [{"table_name": "DATATSET1"}, {"table_name": "DATATSET2"}]

    async def execute(self, query, *args):
        """Mimic execute."""
        return []

    async def close(self):
        """Mimic close."""
        pass

    def transaction(self, *args, **kwargs):
        """Mimic execute."""
        return Transaction(self, *args, **kwargs)


class DatabaseTestCase(asynctest.TestCase):
    """Test database operations."""

    def setUp(self):
        """Initialise BeaconDB object."""
        self._db_url = 'http://url.fi'
        self._db = BeaconDB(self._db_url)
        self._dir = TempDirectory()

    def tearDown(self):
        """Close database connection after tests."""
        self._dir.cleanup_all()

    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg')
    async def test_connection(self, db_mock):
        """Test database URL fetching."""
        await self._db.connection()
        db_mock.connect.assert_called_with(self._db_url)

    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_check_tables(self, db_mock):
        """Test checking tables."""
        db_mock.return_value = Connection()
        await self._db.connection()
        db_mock.assert_called_with(self._db_url)
        result = await self._db.check_tables(['DATATSET1', 'DATATSET2'])
        # No Missing tables
        assert result == []

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_create_tables(self, db_mock, mock_log):
        """Test creating tables."""
        sql = """CREATE TABLE IF NOT EXISTS beacon_data_table (
            id SERIAL,
            dataset_id VARCHAR(200),
            PRIMARY KEY (id));"""
        db_mock.return_value = Connection()
        await self._db.connection()
        db_mock.assert_called_with(self._db_url)
        sql_file = self._dir.write('sql.init', sql.encode('utf-8'))
        await self._db.create_tables(sql_file)
        # Should assert logs
        mock_log.info.assert_called_with('Tables have been created')

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_load_metadata(self, db_mock, mock_log):
        """Test load metadata."""
        metadata = """{"name": "DATASET1",
                    "description": "example dataset number 1",
                    "assemblyId": "GRCh38",
                    "version": "v1",
                    "sampleCount": 2504,
                    "externalUrl": "https://datasethost.org/dataset1",
                    "accessType": "PUBLIC"}"""
        db_mock.return_value = Connection()
        await self._db.connection()
        db_mock.assert_called_with(self._db_url)
        metafile = self._dir.write('data.json', metadata.encode('utf-8'))
        await self._db.load_metadata(metafile)
        # Should assert logs
        mock_log.info.mock_calls = [f'Parsing metadata from {metafile}',
                                    'Metadata has been parsed',
                                    f'Metadata for {metafile} inserted succesffully']

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_load_datafile(self, db_mock, mock_log):
        """Test load_datafile."""
        data = """DATASET1;2947887;1;C;T;;SNP;;1;5008;2504;0.000199681"""
        db_mock.return_value = Connection()
        await self._db.connection()
        db_mock.assert_called_with(self._db_url)
        datafile = self._dir.write('data.csv', data.encode('utf-8'))
        await self._db.load_datafile(datafile)
        # Should assert logs
        mock_log.info.mock_calls = [f'Load variants from file {datafile}',
                                    'Insert variants into the database']

    def test_bad_init(self):
        """Capture error in case of anything wrong with initializing BeaconDB."""
        with self.assertRaises(TypeError):
            BeaconDB()

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_close(self, db_mock, mock_log):
        """Test database URL fetching."""
        db_mock.return_value = Connection()
        await self._db.connection()
        await self._db.close()
        mock_log.info.mock_calls = ['Mark the database connection to be closed',
                                    'The database connection has been closed']


if __name__ == '__main__':
    unittest.main()

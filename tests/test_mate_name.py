import asynctest
from beacon_api.extensions.mate_name import find_fusion, fetch_fusion_dataset
from .test_db_load import Connection


class TestDataQueryFunctions(asynctest.TestCase):
    """Test Data Query functions."""

    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Close database connection after tests."""
        pass

    @asynctest.mock.patch('beacon_api.extensions.mate_name.fetch_fusion_dataset')
    async def test_find_fusion(self, mock_filtered):
        """Test find datasets."""
        mock_filtered.return_value = []
        token = dict()
        token["bona_fide_status"] = False
        result = await find_fusion(None, 'GRCh38', None, 'Y', 'T', 'C', [], token, "NONE")
        self.assertEqual(result, [])
        result_miss = await find_fusion(None, 'GRCh38', None, 'Y', 'T', 'C', [], token, "MISS")
        self.assertEqual(result_miss, [])

    async def test_fetch_fusion_dataset_call(self):
        """Test db call for retrieving mate data."""
        pool = asynctest.CoroutineMock()
        pool.acquire().__aenter__.return_value = Connection()
        assembly_id = 'GRCh38'
        position = (10, 20, None, None, None, None)
        chromosome = 1
        reference = 'A'
        result = await fetch_fusion_dataset(pool, assembly_id, position, chromosome, reference, None, None, None, False)
        # for now it can return empty dataset
        # in order to get a response we will have to mock it
        # in Connection() class
        self.assertEqual(result, [])


if __name__ == '__main__':
    asynctest.main()

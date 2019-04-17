import asynctest
from beacon_api.extensions.mate_name import find_fusion


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


if __name__ == '__main__':
    asynctest.main()

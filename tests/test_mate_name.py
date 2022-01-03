import unittest
from beacon_api.extensions.mate_name import find_fusion


class TestDataQueryFunctions(unittest.IsolatedAsyncioTestCase):
    """Test Data Query functions."""

    @unittest.mock.patch("beacon_api.extensions.mate_name.fetch_fusion_dataset")
    async def test_find_fusion(self, mock_filtered):
        """Test find datasets."""
        mock_filtered.return_value = []
        access_type = list()
        result = await find_fusion(None, "GRCh38", (), "Y", "T", "C", [], access_type, "NONE")
        self.assertEqual(result, [])
        result_miss = await find_fusion(None, "GRCh38", (), "Y", "T", "C", [], access_type, "MISS")
        self.assertEqual(result_miss, [])


if __name__ == "__main__":
    unittest.main()

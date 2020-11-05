import asynctest
import aiohttp
from beacon_api.extensions.mate_name import find_fusion, fetch_fusion_dataset
from .test_db_load import Connection, ConnectionException


class TestDataQueryFunctions(asynctest.TestCase):
    """Test Data Query functions."""

    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Close database connection after tests."""
        pass

    @asynctest.mock.patch("beacon_api.extensions.mate_name.fetch_fusion_dataset")
    async def test_find_fusion(self, mock_filtered):
        """Test find datasets."""
        mock_filtered.return_value = []
        access_type = list()
        result = await find_fusion(None, "GRCh38", (), "Y", "T", "C", [], access_type, "NONE")
        self.assertEqual(result, [])
        result_miss = await find_fusion(None, "GRCh38", (), "Y", "T", "C", [], access_type, "MISS")
        self.assertEqual(result_miss, [])

    async def test_fetch_fusion_dataset_call(self):
        """Test db call for retrieving mate data."""
        pool = asynctest.CoroutineMock()
        db_response = {
            "referenceBases": "",
            "alternateBases": "",
            "variantType": "",
            "referenceName": "Chr38",
            "frequency": 0,
            "callCount": 0,
            "sampleCount": 0,
            "variantCount": 0,
            "start": 0,
            "end": 0,
            "accessType": "PUBLIC",
            "datasetId": "test",
        }
        pool.acquire().__aenter__.return_value = Connection(accessData=[db_response])
        assembly_id = "GRCh38"
        position = (10, 20, None, None, None, None)
        chromosome = 1
        reference = "A"
        result = await fetch_fusion_dataset(pool, assembly_id, position, chromosome, reference, None, None, None, False)
        # for now it can return empty dataset
        # in order to get a response we will have to mock it
        # in Connection() class
        expected = {
            "referenceName": "Chr38",
            "callCount": 0,
            "sampleCount": 0,
            "variantCount": 0,
            "datasetId": "test",
            "referenceBases": "",
            "alternateBases": "",
            "variantType": "",
            "start": 0,
            "end": 0,
            "frequency": 0,
            "info": {"accessType": "PUBLIC"},
            "datasetHandover": [
                {
                    "handoverType": {"id": "CUSTOM", "label": "Variants"},
                    "description": "browse the variants matched by the query",
                    "url": "https://examplebrowser.org/dataset/test/browser/variant/Chr38-1--",
                },
                {
                    "handoverType": {"id": "CUSTOM", "label": "Region"},
                    "description": "browse data of the region matched by the query",
                    "url": "https://examplebrowser.org/dataset/test/browser/region/Chr38-1-1",
                },
                {
                    "handoverType": {"id": "CUSTOM", "label": "Data"},
                    "description": "retrieve information of the datasets",
                    "url": "https://examplebrowser.org/dataset/test/browser",
                },
            ],
        }
        self.assertEqual(result, [expected])

    async def test_fetch_fusion_dataset_call_miss(self):
        """Test db call for retrieving mate miss data."""
        pool = asynctest.CoroutineMock()
        pool.acquire().__aenter__.return_value = Connection()
        assembly_id = "GRCh38"
        position = (10, 20, None, None, None, None)
        chromosome = 1
        reference = "A"
        result_miss = await fetch_fusion_dataset(pool, assembly_id, position, chromosome, reference, None, None, None, True)
        self.assertEqual(result_miss, [])

    async def test_fetch_fusion_dataset_call_exception(self):
        """Test db call for retrieving mate data with exception."""
        pool = asynctest.CoroutineMock()
        pool.acquire().__aenter__.return_value = ConnectionException()
        assembly_id = "GRCh38"
        position = (10, 20, None, None, None, None)
        chromosome = 1
        reference = "A"
        with self.assertRaises(aiohttp.web_exceptions.HTTPInternalServerError):
            await fetch_fusion_dataset(pool, assembly_id, position, chromosome, reference, None, None, None, False)


if __name__ == "__main__":
    asynctest.main()

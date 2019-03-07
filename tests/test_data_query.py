import asynctest
from beacon_api.utils.data_query import filter_exists, transform_record
from beacon_api.utils.data_query import transform_misses, transform_metadata, find_datasets
from datetime import datetime
# from beacon_api.utils.data_query import fetch_dataset_metadata
from beacon_api.utils.data_query import handle_wildcard
# from .test_db_load import Connection


class Record:
    """Record Class.

    Mimic asyncpg Record object.
    """

    def __init__(self, accessType, frequency=None, createDateTime=None, updateDateTime=None,
                 referenceBases=None, alternateBases=None, variantCount=0, variantType=None):
        """Initialise things."""
        self.data = {"accessType": accessType}
        # self.variantCount = variantCount
        if variantCount:
            self.data.update({"variantCount": variantCount})
        if referenceBases:
            self.data.update({"referenceBases": referenceBases})
        if alternateBases:
            self.data.update({"alternateBases": alternateBases})
        if variantType:
            self.data.update({"variantType": variantType})
        if frequency:
            self.data.update({"frequency": frequency})
        if createDateTime:
            self.data.update({"createDateTime": createDateTime})
        if updateDateTime:
            self.data.update({"updateDateTime": updateDateTime})

    def __iter__(self):
        """Return attribute."""
        return iter(self.data)

    def __getitem__(self, name):
        """Return attribute."""
        return self.data[name]

    def keys(self):
        """Return attribute."""
        return self.data.keys()

    def items(self):
        """Return attribute."""
        return self.data.items()

    def values(self):
        """Return attribute."""
        return self.data.values()


class TestDataQueryFunctions(asynctest.TestCase):
    """Test Data Query functions."""

    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Close database connection after tests."""
        pass

    def test_filter_exists(self):
        """Test filtering hits and miss datasets."""
        datasets = [{"exists": True, "name": "DATASET1"}, {"exists": False, "name": "DATASET2"}]
        hits = filter_exists("HIT", datasets)
        misses = filter_exists("MISS", datasets)
        all = filter_exists("ALL", datasets)
        nothing = filter_exists("NONE", datasets)
        self.assertEqual(hits, [{"exists": True, "name": "DATASET1"}])
        self.assertEqual(misses, [{"exists": False, "name": "DATASET2"}])
        self.assertEqual(all, datasets)
        self.assertEqual(nothing, [])

    def test_transform_record(self):
        """Test transform DB record."""
        response = {"frequency": 0.009112876, "info": {"accessType": "PUBLIC"},
                    "referenceBases": "CT", "alternateBases": "AT", "variantCount": 3, "variantType": "MNP"}
        record = Record("PUBLIC", 0.009112875989879, referenceBases="CT", alternateBases="AT", variantCount=3, variantType="MNP")
        result = transform_record(record)
        self.assertEqual(result, response)

    def test_transform_misses(self):
        """Test transform misses record."""
        response = {"referenceBases": '', "alternateBases": '', "variantType": "",
                    "frequency": 0, "callCount": 0, "sampleCount": 0, "variantCount": 0,
                    "info": {"accessType": "PUBLIC"}}
        record = Record("PUBLIC")
        result = transform_misses(record)
        self.assertEqual(result, response)

    def test_transform_metadata(self):
        """Test transform medata record."""
        response = {"createDateTime": "2018-10-20T20:33:40Z", "updateDateTime": "2018-10-20T20:33:40Z",
                    "info": {"accessType": "PUBLIC"}}
        record = Record("PUBLIC", createDateTime=datetime.strptime("2018-10-20 20:33:40+00", '%Y-%m-%d %H:%M:%S+00'),
                        updateDateTime=datetime.strptime("2018-10-20 20:33:40+00", '%Y-%m-%d %H:%M:%S+00'))
        result = transform_metadata(record)
        self.assertEqual(result, response)

    @asynctest.mock.patch('beacon_api.utils.data_query.fetch_filtered_dataset')
    async def test_find_datasets(self, mock_filtered):
        """Test find datasets."""
        mock_filtered.return_value = []
        token = dict()
        token["bona_fide_status"] = False
        result = await find_datasets(None, 'GRCh38', None, 'Y', 'T', 'C', [], token, "NONE")
        self.assertEqual(result, [])

    # async def test_fetch_metadata(self):
    #     """Test fetch_metadata."""
    #     pool = asynctest.CoroutineMock()
    #     pool.acquire.return_value = Connection()
    #     # pool.connection.prepare.return_value = asynctest.CoroutineMock()
    #     result = await fetch_dataset_metadata(pool)
    #     self.assertTrue(False)

    def test_handle_wildcard(self):
        """Test PostgreSQL wildcard handling."""
        sequence1 = 'ATCG'
        sequence2 = 'ATNG'
        sequence3 = 'NNCN'
        self.assertEqual(handle_wildcard(sequence1), ['ATCG'])
        self.assertEqual(handle_wildcard(sequence2), ["%AT_G%"])
        self.assertEqual(handle_wildcard(sequence3), ["%__C_%"])


if __name__ == '__main__':
    asynctest.main()

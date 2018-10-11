import asynctest
from beacon_api.utils.data_query import sql_tuple, filter_exists, transform_record
from beacon_api.utils.data_query import transform_misses, transform_metadata, find_datasets
from datetime import datetime


class Record:
    """Record Class.

    Mimic asyncpg Record object.
    """

    def __init__(self, accessType, frequency=None, createDateTime=None, updateDateTime=None):
        """Initialise things."""
        self.data = {"accessType": accessType}
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

    def test_sql_tuple(self):
        """Test sql tuple from dataset list."""
        single_array = sql_tuple(['DATASET1'])
        multi_array = sql_tuple(['DATASET1', 'DATASET2'])
        self.assertEqual(single_array, "('DATASET1')")
        self.assertEqual(multi_array, "('DATASET1', 'DATASET2')")

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
        response = {"frequency": 0.009112876, "error": None, "info": [{"accessType": "PUBLIC"}]}
        record = Record("PUBLIC", 0.009112875989879)
        result = transform_record(record)
        self.assertEqual(result, response)

    def test_transform_misses(self):
        """Test transform misses record."""
        response = {"frequency": 0, "callCount": 0, "sampleCount": 0, "variantCount": 0,
                    "info": [{"accessType": "PUBLIC"}], "error": None}
        record = Record("PUBLIC")
        result = transform_misses(record)
        print(result)
        self.assertEqual(result, response)

    def test_transform_metadata(self):
        """Test transform medata record."""
        response = {"createDateTime": "2018-10-20T20:33:40Z", "updateDateTime": "2018-10-20T20:33:40Z",
                    "info": [{"accessType": "PUBLIC"}]}
        record = Record("PUBLIC", None, datetime.strptime("2018-10-20 20:33:40+00", '%Y-%m-%d %H:%M:%S+00'),
                        datetime.strptime("2018-10-20 20:33:40+00", '%Y-%m-%d %H:%M:%S+00'))
        result = transform_metadata(record)
        print(result)
        self.assertEqual(result, response)

    @asynctest.mock.patch('beacon_api.utils.data_query.fetch_filtered_dataset')
    async def test_find_datasets(self, mock_filtered):
        """Test find datasets."""
        mock_filtered.return_value = []
        token = dict()
        token["bona_fide_status"] = False
        result = await find_datasets(None, None, 'T', 'C', [], token)
        self.assertEqual(result, [])


if __name__ == '__main__':
    asynctest.main()

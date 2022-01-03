import unittest
from unittest import mock
from beacon_api.utils.data_query import filter_exists, transform_record
from beacon_api.utils.data_query import transform_misses, transform_metadata, find_datasets, add_handover
from beacon_api.extensions.handover import make_handover
from datetime import datetime
from beacon_api.utils.data_query import handle_wildcard


class Record:
    """Record Class.

    Mimic asyncpg Record object.
    """

    def __init__(
        self,
        accessType,
        frequency=None,
        createDateTime=None,
        updateDateTime=None,
        referenceBases=None,
        alternateBases=None,
        start=None,
        end=None,
        variantCount=0,
        variantType=None,
    ):
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
        if start:
            self.data.update({"start": start})
        if end:
            self.data.update({"end": end})
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


class TestDataQueryFunctions(unittest.IsolatedAsyncioTestCase):
    """Test Data Query functions."""

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
        response = {
            "frequency": 0.009112876,
            "info": {"accessType": "PUBLIC"},
            "referenceBases": "CT",
            "alternateBases": "AT",
            "start": 10,
            "end": 12,
            "variantCount": 3,
            "variantType": "MNP",
        }
        record = Record(
            "PUBLIC",
            0.009112875989879,
            referenceBases="CT",
            alternateBases="AT",
            start=10,
            end=12,
            variantCount=3,
            variantType="MNP",
        )
        result = transform_record(record)
        self.assertEqual(result, response)

    def test_transform_misses(self):
        """Test transform misses record."""
        response = {
            "referenceBases": "",
            "alternateBases": "",
            "variantType": "",
            "frequency": 0,
            "callCount": 0,
            "sampleCount": 0,
            "variantCount": 0,
            "start": 0,
            "end": 0,
            "info": {"accessType": "PUBLIC"},
        }
        record = Record("PUBLIC")
        result = transform_misses(record)
        self.assertEqual(result, response)

    def test_transform_metadata(self):
        """Test transform medata record."""
        response = {
            "createDateTime": "2018-10-20T20:33:40Z",
            "updateDateTime": "2018-10-20T20:33:40Z",
            "info": {"accessType": "PUBLIC"},
        }
        record = Record(
            "PUBLIC",
            createDateTime=datetime.strptime("2018-10-20 20:33:40+00", "%Y-%m-%d %H:%M:%S+00"),
            updateDateTime=datetime.strptime("2018-10-20 20:33:40+00", "%Y-%m-%d %H:%M:%S+00"),
        )
        result = transform_metadata(record)
        self.assertEqual(result, response)

    def test_add_handover(self):
        """Test that add handover."""
        # Test that the handover actually is added
        handovers = [{"handover1": "info"}, {"handover2": "url"}]
        record = {
            "datasetId": "test",
            "referenceName": "22",
            "referenceBases": "A",
            "alternateBases": "C",
            "start": 10,
            "end": 11,
            "variantType": "SNP",
        }
        with mock.patch("beacon_api.extensions.handover.make_handover", return_value=handovers):
            result = add_handover(record)
        record["datasetHandover"] = handovers
        self.assertEqual(result, record)

    def test_make_handover(self):
        """Test make handover."""
        paths = [("lab1", "desc1", "path1"), ("lab2", "desc2", "path2")]
        result = make_handover(paths, ["id1", "id2", "id1"])
        # The number of handovers = number of paths * number of unique datasets
        self.assertEqual(len(result), 4)
        self.assertIn("path1", result[0]["url"])
        self.assertEqual(result[0]["description"], "desc1")

    @unittest.mock.patch("beacon_api.utils.data_query.fetch_filtered_dataset")
    async def test_find_datasets(self, mock_filtered):
        """Test find datasets."""
        mock_filtered.return_value = []
        token = dict()
        token["bona_fide_status"] = False
        result = await find_datasets(None, "GRCh38", None, "Y", "T", "C", [], token, "NONE")
        self.assertEqual(result, [])
        # setting ALL should cover MISS call as well
        result_all = await find_datasets(None, "GRCh38", None, "Y", "T", "C", [], token, "ALL")
        self.assertEqual(result_all, [])

    def test_handle_wildcard(self):
        """Test PostgreSQL wildcard handling."""
        sequence1 = "ATCG"
        sequence2 = "ATNG"
        sequence3 = "NNCN"
        self.assertEqual(handle_wildcard(sequence1), ["ATCG"])
        self.assertEqual(handle_wildcard(sequence2), ["%AT_G%"])
        self.assertEqual(handle_wildcard(sequence3), ["%__C_%"])


if __name__ == "__main__":
    unittest.main()

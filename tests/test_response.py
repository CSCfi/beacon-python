from beacon_api.api.info import beacon_info
from beacon_api.api.query import query_request_handler
import asynctest


class TestBasicFunctions(asynctest.TestCase):
    """Test supporting functions."""

    @asynctest.mock.patch('beacon_api.api.info.fetch_dataset_metadata')
    async def test_beacon_info(self, db_metadata):
        """Test database URL fetching."""
        pool = asynctest.CoroutineMock()
        await beacon_info('localhost', pool)
        db_metadata.assert_called()

    @asynctest.mock.patch('beacon_api.api.query.find_datasets')
    @asynctest.mock.patch('beacon_api.api.query.filter_exists')
    async def test_beacon_query(self, data_filter, data_find):
        """Test database URL fetching."""
        pool = asynctest.CoroutineMock()
        request = {}
        params = pool, 'POST', request, {'bona_fide_status': True}, "localhost"
        await query_request_handler(params)
        data_find.assert_called()
        data_filter.assert_called()

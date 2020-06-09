import integ_test as tests
from integ_test import LOG
import inspect
import asyncio


async def main() -> None:
    """Run the tests."""
    LOG.debug('Start integration tests')
    # tests 18, 19 and 20 are also tested in the unit tests
    # redundant, but later we may want to validate against JSON schema
    all_functions = inspect.getmembers(tests, inspect.isfunction)
    for x in all_functions:
        await x[1]()
    LOG.debug('All integration tests have passed')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

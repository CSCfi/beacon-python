"""Logging formatting."""

import logging
# import inspect

# TO DO: do some proper logs
# callerframe = inspect.stack()[1][0]
# name = callerframe.f_globals["__name__"]
formatting = '[%(asctime)s][%(name)s][%(process)d %(processName)s][%(levelname)-8s] (L:%(lineno)s) %(funcName)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=formatting)

LOG = logging.getLogger("testing")

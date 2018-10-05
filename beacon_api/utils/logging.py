import logging
import os
# import inspect

# Sets the logging level from environmental variable.
LOGGING_LVL = os.environ.get('LOGGING_LVL', 'DEBUG')
# callerframe = inspect.stack()[1][0]
# name = callerframe.f_globals["__name__"]
formatting = '[%(asctime)s][%(name)s][%(process)d %(processName)s][%(levelname)-8s] (L:%(lineno)s) %(funcName)s: %(message)s'
if LOGGING_LVL == 'DEBUG':
    logging.basicConfig(level=logging.DEBUG, format=formatting)
elif LOGGING_LVL == 'INFO':
    logging.basicConfig(level=logging.INFO, format=formatting)
elif LOGGING_LVL == 'WARNING':
    logging.basicConfig(level=logging.WARNING, format=formatting)
elif LOGGING_LVL == 'CRITICAL':
    logging.basicConfig(level=logging.CRITICAL, format=formatting)

LOG = logging.getLogger("testing")

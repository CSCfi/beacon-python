"""Logging formatting."""

import logging

# Keeping it simple with the logging formatting

formatting = '[%(asctime)s][%(name)s][%(process)d %(processName)s][%(levelname)-8s] (L:%(lineno)s) %(module)s | %(funcName)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=formatting)

LOG = logging.getLogger("beacon")

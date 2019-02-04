"""Permissions Module.

Module for getting permissions to CONTROLLED datasets.
This module was designed to be addon based, where users of the beacon python app can add their own modules for handling ``CONTROLLED`` permissions to datasets.

Each file added in this module will consist of a function for parsing a permissions claim
from a JWT token. Then this function will be added to ``utils.validate`` module in order
to pass permissions when retrieving datasets from Database.
"""

"""Permissions Module.

Module for getting permissions to datasets, more precisely ``CONTROLLED`` datasets.
This module was designed to be addon based, where users of the ``beacon-python`` app can
write their implementation for parsing a specific JWT token claim
that contains ``CONTROLLED`` permissions to datasets.

Each file added in this module will consist of a function for parsing a permissions claim
from a JWT token. Then this function MUST be added to ``utils.validate_jwt`` module in order
to pass permissions when retrieving datasets from the database.

To avoid collisions check that your claim for permissions does not conflict with existing ones:
https://www.iana.org/assignments/jwt/jwt.xhtml
"""

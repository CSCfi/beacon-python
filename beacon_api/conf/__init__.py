"""Beacon Application Configuration."""

import os
from configparser import ConfigParser
from collections import namedtuple


def parse_config_file(path):
    """Parse configuration file."""
    config = ConfigParser()
    config.read(path)
    config_vars = {
        'title': config.get('beacon_general_info', 'title'),
        'version': config.get('beacon_general_info', 'version'),
        'author': config.get('beacon_general_info', 'author'),
        'license': config.get('beacon_general_info', 'license'),
        'copyright': config.get('beacon_general_info', 'copyright'),
        'apiVersion': config.get('beacon_api_info', 'apiVersion'),
        'beaconId': config.get('beacon_api_info', 'beaconId'),
        'description': config.get('beacon_api_info', 'description'),
        'url': config.get('beacon_api_info', 'url'),
        'alturl': config.get('beacon_api_info', 'alturl'),
        'createtime': config.get('beacon_api_info', 'createtime'),
        'org_id': config.get('organisation_info', 'org_id'),
        'org_name': config.get('organisation_info', 'org_name'),
        'org_description': config.get('organisation_info', 'org_description'),
        'org_address': config.get('organisation_info', 'org_address'),
        'org_welcomeUrl': config.get('organisation_info', 'org_welcomeUrl'),
        'org_contactUrl': config.get('organisation_info', 'org_contactUrl'),
        'org_logoUrl': config.get('organisation_info', 'org_logoUrl'),
        'org_info': config.get('organisation_info', 'org_info')
    }
    return namedtuple("Config", config_vars.keys())(*config_vars.values())


CONFIG_INFO = parse_config_file(os.environ.get('CONFIG_FILE', os.path.join(os.path.dirname(__file__), 'config.ini')))


def parse_oauth2_config_file(path):
    """Parse configuration file."""
    config = ConfigParser()
    config.read(path)
    config_vars = {
        'server': config.get('oauth2', 'server'),
        'issuers': config.get('oauth2', 'issuers'),
        'bona_fide': config.get('oauth2', 'bona_fide')
    }
    return namedtuple("Config", config_vars.keys())(*config_vars.values())


OAUTH2_CONFIG = parse_oauth2_config_file(os.environ.get('CONFIG_FILE', os.path.join(os.path.dirname(__file__), 'config.ini')))

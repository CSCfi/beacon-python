"""The beacon package contains code to start an EGA Beacon API.

. note:: In this file is where one would register information about the ``Beacon``.
"""
import os
import datetime

from .conf.config import parse_configuration_file

CONFIG = parse_configuration_file(os.environ.get('CONFIG_FILE', './beacon_api/conf/config.ini'))

__title__ = CONFIG.title
__version__ = CONFIG.version
__author__ = CONFIG.author
__license__ = CONFIG.license
__copyright__ = CONFIG.copyright


__apiVersion__ = CONFIG.apiVersion
__beaconId__ = CONFIG.beaconId
__description__ = CONFIG.description
__url__ = CONFIG.url
__alturl__ = CONFIG.alturl
__createtime__ = CONFIG.createtime
__updatetime__ = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')  # Every restart of the application means an update to it


__org_id__ = CONFIG.org_id
__org_name__ = CONFIG.org_name
__org_description__ = CONFIG.org_description
__org_address__ = CONFIG.org_address
__org_welcomeUrl__ = CONFIG.org_welcomeUrl
__org_contactUrl__ = CONFIG.org_contactUrl
__org_logoUrl__ = CONFIG.org_logoUrl
__org_info__ = [{'orgInfo': CONFIG.org_info}]

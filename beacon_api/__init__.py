"""The beacon package contains code to start an EGA Beacon API.

. note:: In this file is where one would register information about the ``Beacon``.
"""
import datetime

from .conf import CONFIG_INFO

__title__ = CONFIG_INFO.title
__version__ = CONFIG_INFO.version
__author__ = CONFIG_INFO.author
__license__ = CONFIG_INFO.license
__copyright__ = CONFIG_INFO.copyright

__apiVersion__ = CONFIG_INFO.apiVersion
__beaconId__ = CONFIG_INFO.beaconId
__description__ = CONFIG_INFO.description
__url__ = CONFIG_INFO.url
__alturl__ = CONFIG_INFO.alturl
__createtime__ = CONFIG_INFO.createtime
__updatetime__ = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')  # Every restart of the application means an update to it


__org_id__ = CONFIG_INFO.org_id
__org_name__ = CONFIG_INFO.org_name
__org_description__ = CONFIG_INFO.org_description
__org_address__ = CONFIG_INFO.org_address
__org_welcomeUrl__ = CONFIG_INFO.org_welcomeUrl
__org_contactUrl__ = CONFIG_INFO.org_contactUrl
__org_logoUrl__ = CONFIG_INFO.org_logoUrl
__org_info__ = {'orgInfo': CONFIG_INFO.org_info}

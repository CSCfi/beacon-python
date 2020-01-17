"""The ``beacon_api`` package contains code to start an EGA Beacon API.

.. note:: In this file the information about the ``Beacon`` is registered.
         The information is parsed from :file:`beacon_api.conf.config.ini`
"""
import datetime

from .conf import CONFIG_INFO, SAMPLE_QUERIES

__title__ = CONFIG_INFO.title
__version__ = CONFIG_INFO.version
__author__ = CONFIG_INFO.author
__license__ = CONFIG_INFO.license
__copyright__ = CONFIG_INFO.copyright
__docs_url__ = CONFIG_INFO.docs_url
__handover_drs__ = CONFIG_INFO.handover_drs.rstrip("/")
__handover_datasets__ = CONFIG_INFO.handover_datasets
__handover_beacon__ = CONFIG_INFO.handover_beacon
__handover_base__ = CONFIG_INFO.handover_base

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

__sample_queries__ = SAMPLE_QUERIES

# GA4GH Discovery
__service_type__ = {'group': f'{CONFIG_INFO.service_group}',
                    'artifact': f'{CONFIG_INFO.service_artifact}',
                    'version': f'{__apiVersion__}'}
__service_env__ = CONFIG_INFO.environment

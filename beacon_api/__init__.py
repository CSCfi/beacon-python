"""The beacon package contains code to start an EGA Beacon API.

. note:: In this file is where one would register information about the ``Beacon``.
"""
import datetime


__title__ = 'EGA Beacon'
__version__ = VERSION = '1.0.0'
__author__ = 'CSC developers'
__license__ = 'Apache 2.0'
__copyright__ = 'CSC - IT Center for Science'


__apiVersion__ = "1.0.0"
__beaconId__ = "ega-beacon"
__description__ = f'This Beacon is based on the GA4GH Beacon API {__apiVersion__}'
__url__ = 'https://ega-archive.org/'
__alturl__ = 'https://ega-archive.org/beacon/#/'
__createtime__ = '2018-07-25T00:00:00Z'  # Fixed date, based when the beacon was first created
__updatetime__ = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')  # Every restart of the application means an update to it


__org_id__ = 'CSC'
__org_name__ = __copyright__
__org_description__ = """CSC – Finnish expertise in ICT for research, education, culture and public administration."""
__org_address__ = None
__org_welcomeUrl__ = 'https://www.csc.fi/'
__org_contactUrl__ = None
__org_logoUrl__ = 'https://www.csc.fi/documents/10180/161914/CSC_2012_LOGO_RGB_72dpi.jpg'
__org_info__ = None

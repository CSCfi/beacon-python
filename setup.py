from setuptools import setup
from beacon_api import __license__, __version__, __author__


setup(name='beacon_api',
      version=__version__,
      url='',
      project_urls={
          'Source': 'https://github.com/CSCfi/beacon-python',
      },
      license=__license__,
      author=__author__,
      author_email='',
      description='Beacon Python API',
      long_description="",
      packages=['beacon_api', 'beacon_api/utils', 'beacon_api/conf', 'beacon_api/schemas', 'beacon_api/api'],
      package_data={
        # If any package contains *.json, include them:
        '': ['*.json']
      },
      entry_points={
          'console_scripts': [
              'beacon=beacon_api.app:main'
          ]
      },
      platforms='any',)

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
      # If any package contains *.json, include them:
      package_data={'': ['*.json']},
      entry_points={
          'console_scripts': [
              'beacon=beacon_api.app:main',
              'beacon_init=beacon_api.utils.db_load:main'
          ]
      },
      platforms='any',
      extras_require={
          'docs': [
              'sphinx >= 1.4',
              'sphinx_rtd_theme']}
      )

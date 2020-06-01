from setuptools import find_packages, setup
from beacon_api import __license__, __version__, __author__, __description__


setup(name='beacon_api',
      version=__version__,
      url='https://beacon-python.rtfd.io/',
      project_urls={
          'Source': 'https://github.com/CSCfi/beacon-python',
      },
      license=__license__,
      author=__author__,
      author_email='',
      description=__description__,
      long_description="",
      packages=find_packages(exclude=["tests", "docs"]),
      # If any package contains *.json, or config in *.ini, include them:
      package_data={'': ['*.json', '*.ini']},
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'beacon=beacon_api.app:main',
              'beacon_init=beacon_api.utils.db_load:main'
          ]
      },
      platforms='any',
      classifiers=[
          'Development Status :: 5 - Production/Stable',

          'Intended Audience :: Developers',
          'Intended Audience :: Healthcare Industry',
          'Intended Audience :: Information Technology',
          'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
          'Topic :: Scientific/Engineering :: Bio-Informatics',

          'License :: OSI Approved :: Apache Software License',

          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      install_requires=['asyncpg', 'aiohttp', 'authlib', 'aiohttp_cors',
                        'jsonschema', 'gunicorn>=20.0.1',
                        'ujson', 'uvloop', 'aiocache', 'ujson', 'aiomcache'],
      extras_require={
          'vcf': ["cyvcf2==0.10.1; python_version < '3.7'", 'numpy',
                  "cyvcf2; python_version >= '3.7'", 'Cython'],
          'test': ['coverage==4.5.4', 'pytest<5.4', 'pytest-cov',
                   'coveralls', 'testfixtures', 'tox',
                   'flake8', 'flake8-docstrings', 'asynctest', 'aioresponses'],
          'docs': [
              'sphinx >= 1.4',
              'sphinx_rtd_theme']}
      )

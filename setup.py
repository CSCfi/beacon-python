from setuptools import setup

setup(name='beacon_api',
      version='0.0.1',
      url='',
      project_urls={
          'Source': 'https://github.com/CSCfi/beacon-python',
      },
      license='Apache License 2.0',
      author='',
      author_email='',
      description='Beacon Python API',
      long_description="",
      packages=['beacon_api', 'beacon_api/utils', 'beacon_api/conf'],
      entry_points={
          'console_scripts': [
              'beacon=beacon_api.wsgi:main'
          ]
      },
      platforms='any',)

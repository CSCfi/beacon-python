from setuptools import find_packages, setup
from beacon_api import __license__, __version__, __author__, __description__


setup(
    name="beacon_api",
    version=__version__,
    url="https://beacon-python.rtfd.io/",
    project_urls={
        "Source": "https://github.com/CSCfi/beacon-python",
    },
    license=__license__,
    author=__author__,
    author_email="",
    description=__description__,
    long_description="",
    packages=find_packages(exclude=["tests", "docs"]),
    # If any package contains *.json, or config in *.ini, include them:
    package_data={"": ["*.json", "*.ini"]},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "beacon=beacon_api.app:main",
            "beacon_init=beacon_api.utils.db_load:main",
        ]
    },
    platforms="any",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Information Technology",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[
        "asyncpg==0.24.0",
        "aiohttp==3.7.4.post0",
        "Authlib==0.15.5",
        "aiohttp-cors==0.7.0",
        "jsonschema==3.2.0; python_version < '3.7'",
        "jsonschema==4.2.1; python_version >= '3.7'",
        "gunicorn==20.1.0",
        "uvloop==0.14.0; python_version < '3.7'",
        "uvloop==0.16.0; python_version >= '3.7'",
        "cyvcf2==0.10.1; python_version < '3.7'",
        "cyvcf2; python_version >= '3.7'",
        "aiocache==0.11.1",
        "ujson==4.2.0",
        "aiomcache==0.6.0",
    ],
    extras_require={
        "vcf": [
            "cyvcf2==0.10.1; python_version < '3.7'",
            "numpy==1.21.4",
            "cyvcf2; python_version >= '3.7'",
            "Cython==0.29.24",
        ],
        "test": [
            "coverage==6.1.2",
            "pytest<6.3",
            "pytest-cov==3.0.0",
            "testfixtures==6.18.3",
            "tox==3.24.4",
            "flake8==4.0.1",
            "flake8-docstrings==1.6.0",
            "asynctest==0.13.0",
            "aioresponses==0.7.2",
            "black==21.11b1",
        ],
        "docs": ["sphinx >= 1.4", "sphinx_rtd_theme==1.0.0"],
    },
)

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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=[
        "asyncpg==0.28.0",
        "aiohttp==3.8.4",
        "Authlib==1.2.1",
        "aiohttp-cors==0.7.0",
        "jsonschema==4.18.0",
        "gunicorn==20.1.0",
        "uvloop==0.17.0",
        "cyvcf2==0.30.18",
        "aiocache==0.11.1",
        "ujson==5.8.0",
    ],
    extras_require={
        "vcf": [
            "numpy==1.25.1",
            "cyvcf2==0.30.18",
            "Cython==0.29.35",
        ],
        "test": [
            "coverage==7.2.7",
            "pytest<7.5",
            "pytest-cov==4.1.0",
            "testfixtures==7.1.0",
            "tox==4.6.3",
            "flake8==6.0.0",
            "flake8-docstrings==1.7.0",
            "aioresponses==0.7.4",
            "black==23.3.0",
        ],
        "docs": ["sphinx >= 1.4", "sphinx_rtd_theme==1.2.2"],
    },
)

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
        "asyncpg==0.27.0",
        "aiohttp==3.8.3",
        "Authlib==1.2.0",
        "aiohttp-cors==0.7.0",
        "jsonschema==4.17.3",
        "gunicorn==20.1.0",
        "uvloop==0.17.0",
        "cyvcf2==0.30.18",
        "aiocache==0.11.1",
        "ujson==5.6.0",
    ],
    extras_require={
        "vcf": [
            "numpy==1.24.0",
            "cyvcf2==0.30.18",
            "Cython==0.29.32",
        ],
        "test": [
            "coverage==6.5.0",
            "pytest<7.3",
            "pytest-cov==4.0.0",
            "testfixtures==7.0.4",
            "tox==4.0.8",
            "flake8==6.0.0",
            "flake8-docstrings==1.6.0",
            "aioresponses==0.7.3",
            "black==22.12.0",
        ],
        "docs": ["sphinx >= 1.4", "sphinx_rtd_theme==1.1.1"],
    },
)

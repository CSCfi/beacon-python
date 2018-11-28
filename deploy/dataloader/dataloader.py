"""1000 Genomes Dataset Autoloader."""

import urllib.request
import logging
import os
import time

from ftplib import FTP
from subprocess import call
from math import ceil

# LOGGING
formatting = '[%(asctime)s][%(name)s][%(process)d %(processName)s][%(levelname)-8s] (L:%(lineno)s) %(module)s | %(funcName)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=formatting)
LOG = logging.getLogger("DATALOADER")


def main():
    """Run data loader."""
    start_time = time.time()  # runtime start

    # FTP details
    FTP_URL = os.environ.get('FTP_URL', 'ftp.1000genomes.ebi.ac.uk')
    FTP_DIR = os.environ.get('FTP_DIR', '/vol1/ftp/release/20130502/')

    # Connect to FTP
    LOG.info(f'Connect to FTP repository at {FTP_URL}')
    ftp = FTP(FTP_URL)
    ftp.login()
    ftp.cwd(FTP_DIR)

    # Get listing of directory for .vcf.gz files
    LOG.info('Retrieve datafile listing from FTP repository')
    directory = ftp.nlst('*.vcf.gz')
    directory = [d for d in directory if 'chr' in d]  # filter to contain only chromosome files
    total_size = 0
    LOG.info('Calculating total disk space required')
    for datafile in directory:
        total_size += ftp.size(datafile)
    print(f'{len(directory)} files found ({ceil(total_size/1073741824)} GB)')

    # Start tasks
    expected_tasks = len(directory)*2  # 2 tasks per file: download and parse
    LOG.info(f'Workflow started :: {expected_tasks} tasks to do')
    completed_tasks = 0  # counter

    LOG.info('Start downloading datafiles')
    for datafile in directory:
        try:
            completed_tasks += 1
            LOG.info(f'[{completed_tasks}/{expected_tasks}] Downloading {datafile}')
            # download datafile from repository
            #                          address                            destination
            urllib.request.urlretrieve('ftp://'+FTP_URL+FTP_DIR+datafile, '/app/data/'+datafile)
        except Exception as e:
            completed_tasks -= 1
            LOG.error(f'ERROR AT DOWNLOAD :: {e}')
    LOG.info('Datafiles have been downloaded')

    LOG.info('Start processing datafiles')
    for datafile in directory:
        try:
            completed_tasks += 1
            LOG.info(f'[{completed_tasks}/{expected_tasks}] Parsing {datafile}')
            # call beacon_init command from python
            #      shell cmd      datafile                  metadata
            call(["beacon_init", f"/app/data/{datafile}", "/app/example_metadata.json"])
        except Exception as e:
            completed_tasks -= 1
            LOG.error(f'ERROR AT PARSING :: {e}')
    LOG.info('Datafiles have been processed')

    LOG.info(f'Workflow finished :: {completed_tasks}/{expected_tasks} tasks completed')

    LOG.info(f'Runtime: {round(time.time() - start_time, 2)} s')


if __name__ == '__main__':
    LOG.info('Start dataloader')
    main()

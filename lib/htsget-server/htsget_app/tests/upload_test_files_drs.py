import os
from pathlib import Path
import configparser
import requests


config = configparser.ConfigParser()
config.read(Path('./config.ini'))

LOCAL_FILE_PATH = config['paths']['LocalFilesPath']
DRS_URL = config['paths']['DRSPath']

TEST_FILES = [
    'NA18537.vcf.gz',
    'NA18537.vcf.gz.tbi',
    'NA20787.vcf.gz',
    'NA20787.vcf.gz.tbi'
]


for filename in TEST_FILES:
    file_path = Path(os.path.join(LOCAL_FILE_PATH, filename)).expanduser().resolve()
    url = f"{DRS_URL}/ingest"

    res = requests.post(url, json={'path': str(file_path)})
    res.raise_for_status()

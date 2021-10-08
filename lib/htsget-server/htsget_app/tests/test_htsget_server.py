import configparser
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib import parse

import pytest
import requests
from pysam import AlignmentFile, TabixFile, VariantFile

config = configparser.ConfigParser()
config.read(Path('./config.ini'))

BASE_PATH = config['DEFAULT']['BasePath']
PORT = config['DEFAULT']['Port']
HOST = f"http://localhost:{PORT}{BASE_PATH}"
FILE_RETRIEVAL = config['DEFAULT']['FileRetrieval']
LOCAL_FILE_PATH = config['paths']['LocalFilesPath']
MINIO_FILE_PATH = config['paths']['MinioFilePath']

FILE_PATH = LOCAL_FILE_PATH


def invalid_start_end_data():
    return [(17123456, 23588), (9203, 42220938)]


@pytest.mark.parametrize('start, end', invalid_start_end_data())
def test_invalid_start_end(start, end):
    """
    Should return a 400 error if end is smaller than start
    """
    url_v = f"{HOST}/variants/NA18537?referenceName=21&start={start}&end={end}"
    url_r = f"{HOST}/reads/NA18537?referenceName=21&start={start}&end={end}"

    res_v = requests.get(url_v)
    print(res_v)
    res_r = requests.get(url_r)

    if end < start:
        assert res_v.status_code == 400
        assert res_r.status_code == 400
    else:
        assert True


def existent_file_test_data():
    return [('NA18537', 200), ('NA20787', 200), ('HG203245', 404), ('NA185372', 404)]


@pytest.mark.parametrize('id, expected_status', existent_file_test_data())
def test_existent_file(id, expected_status):
    """
    Should fail with expected error if a file does not exist for given ID
    """
    url_v = f"{HOST}/variants/{id}?referenceName=21&start=10235878&end=45412368"
    url_r = f"{HOST}/reads/{id}?referenceName=21&start=10235878&end=45412368"

    res_v = requests.get(url_v)
    res_r = requests.get(url_r)
    assert res_v.status_code == expected_status or res_r.status_code == expected_status


def test_file_without_start_end_data():
    return [('NA18537', '21', '.vcf.gz', 'variant'), ('NA20787', '21', '.vcf.gz', 'variant')]


@pytest.mark.parametrize('id, referenceName, file_extension, file_type', test_file_without_start_end_data())
def test_file_without_start_end(id, referenceName, file_extension, file_type):
    url = f"{HOST}/data/{id}?referenceName={referenceName}"
    res = requests.get(url)

    file_name = f"{id}{file_extension}"
    path = f"./{file_name}"
    f = open(path, 'wb')
    f.write(res.content)

    file_one = None
    file_two = None
    if file_type == "variant":
        file_one = VariantFile(path)
        file_two = VariantFile(f"{FILE_PATH}/{file_name}")
    elif file_type == "read":
        file_one = AlignmentFile(path)
        file_two = AlignmentFile(f"{FILE_PATH}/{file_name}")
    equal = True
    for x, y in zip(file_one.fetch(), file_two.fetch(contig=referenceName)):
        if x != y:
            equal = False
            os.remove(path)
            assert equal
    os.remove(path)
    assert equal


def test_pull_slices_data():
    return [
        ({"referenceName": "21",
          "start": 92033, "end": 32345678}, 'NA18537', ".vcf.gz", "variant")
    ]


@pytest.mark.parametrize('params, id_, file_extension, file_type', test_pull_slices_data())
def test_pull_slices(params, id_, file_extension, file_type):
    url = f"{HOST}/{file_type}s/{id_}"    
    res = requests.get(url, params)
    res = res.json()    
    urls = res['htsget']['urls']

    f_index = 0
    f_name = f"{id_}{file_extension}"
    equal = True
    for i in range(len(urls)):
        url = urls[i]['url']
        res = requests.get(url)

        f_slice_name = f"{id_}_{i}{file_extension}"
        f_slice_path = f"./{f_slice_name}"
        f_slice = open(f_slice_path, 'wb')
        f_slice.write(res.content)
        f_slice = None
        f = None
        if file_type == "variant":
            f_slice = VariantFile(f_slice_path)
            f = VariantFile(f"{FILE_PATH}/{f_name}")
        elif file_type == "read":
            f_slice = AlignmentFile(f_slice_path)
            f = AlignmentFile(f"{FILE_PATH}/{f_name}")

        # get start index for original file
        for rec in f_slice.fetch():
            f_index = rec.pos - 1
            break
        # compare slice and file line by line
        for x, y in zip(f_slice.fetch(), f.fetch(contig=params['referenceName'], start=f_index)):
            if x != y:
                equal = False
                assert equal
        os.remove(f_slice_path)
    assert equal

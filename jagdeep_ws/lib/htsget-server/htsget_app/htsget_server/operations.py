import os
import configparser
from pathlib import Path
from tempfile import NamedTemporaryFile
import sqlite3
import requests
from flask import request, send_file
from flask import send_file
from pysam import VariantFile, AlignmentFile
from minio import Minio
from minio.error import ResponseError
from database import MyDatabase


config = configparser.ConfigParser()
config.read(Path('./config.ini'))

BASE_PATH = config['DEFAULT']['BasePath']
LOCAL_FILES_PATH = config['paths']['LocalFilesPath']
LOCAL_DB_PATH = config['paths']['LocalDBPath']
TEMPORARY_FILES_PATH = config['paths']['TemporaryFilesPath']
CHUNK_SIZE = int(config['DEFAULT']['ChunkSize'])
FILE_RETRIEVAL = config['DEFAULT']['FileRetrieval']
DRS_URL = config['paths']['DRSPath']
MINIO_END_POINT = config['minio']['EndPoint']
MINIO_ACCESS_KEY = config['minio']['AccessKey']
MINIO_SECRET_KEY = config['minio']['SecretKey']
DATABASE = config['DEFAULT']['DataBase']
DB_PATH = config['paths']['DBPath']


""" Helper Functions"""
def _get_file_by_id(id):
    """
    Returns an array of tuples of a file based on ID from DBV

    :param id: The id of the file
    """
    query = """SELECT * FROM  files WHERE id = (:id) LIMIT 1"""
    param_obj = {'id': id}
    db = MyDatabase(DB_PATH)
    return db.get_data(query, param_obj)


def file_exists_db(id):
    file = _get_file_by_id(id)  # returns an array of tuples0
    return (len(file) != 0)


def search_drs(id):
    drs_objects = {}
    url = f"{DRS_URL}/search?fuzzy_name={id}"

    res = requests.get(url)
    res.raise_for_status()
    data = res.json()

    # TODO: what happens when for a single name, we have both a vcf & bcf?
    # TODO: also do we cover every possible extension?
    for obj in data:
        if any(ext in obj['name'].lower() for ext in ['tbi', 'bai']):
            if 'index_file' in drs_objects:
                print('We have found multiple index files for this DRS query')
            else:
                drs_objects['index_file'] = obj
        elif any(ext in obj['name'].lower() for ext in ['vcf', 'bcf', 'bam', 'cram']):
            if 'file' in drs_objects:
                print('We have found multiple files for this DRS query')
            else:
                drs_objects['file'] = obj

    if 'file' in drs_objects:
        return drs_objects
    else:
        return None


def _get_file_format_drs(drs_objects):
    # TODO: should we provide custom mime_type in DRS?
    if 'vcf' in drs_objects['file']['name'].lower():
        return 'VCF'
    elif 'bcf' in drs_objects['file']['name'].lower():
        return 'BCF'
    elif 'bam' in drs_objects['file']['name'].lower():
        return 'BAM'
    elif 'cram' in drs_objects['file']['name'].lower():
        return 'CRAM'
    else:
        return None


def _download_minio_file(drs_objects):
    """
    Download file from minio
    - assume indexed file is stored in minio and DRS
    """
    if '127.0.0.1' in MINIO_END_POINT or 'localhost' in MINIO_END_POINT:
        secure = False
    else:
        secure = True

    client = Minio(
        MINIO_END_POINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=secure
    )
    file_url = ""
    index_file_url = ""

    for method in drs_objects['file']['access_methods']:
        if method['type'] == 's3':
            file_url = method['access_url']['url']

    if not file_url:
        raise Exception('Cannot find proper minio (s3) access method in the DRS objects queried')

    if 'index_file' in drs_objects:
        for method in drs_objects['index_file']['access_methods']:
            if method['type'] == 's3':
                index_file_url = method['access_url']['url']
    else:
        index_file_url = None

    bucket = file_url.split('/')[-2]
    file_name = file_url.split('/')[-1]
    file_path = os.path.join(LOCAL_FILES_PATH, file_name)

    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
    else:
        file_size = None

    # Only download the file if the local size and DRS size differ
    if not file_size or file_size != drs_objects['file']['size']:
        try:
            client.fget_object(bucket, file_name, file_path)
        except ResponseError as err:
            raise Exception(err)

    if index_file_url:
        index_file_name = index_file_url.split('/')[-1]
        index_file_path = os.path.join(LOCAL_FILES_PATH, index_file_name)

        if os.path.exists(index_file_path):
            index_file_size = os.path.getsize(index_file_path)
        else:
            index_file_size = None

        if not index_file_size or index_file_size != drs_objects['index_file']['size']:
            try:
                client.fget_object(bucket, index_file_name, index_file_path)
            except ResponseError as err:
                raise Exception(err)
    else:
        index_file_path = None

    return file_path, index_file_path


def _create_slice(arr, id, referenceName, slice_start, slice_end):
    """
    Creates slice and appends it to array of urls

    :param arr: The array to store urls
    :param id: ID of the file
    :param referenceName: The Chromosome number
    :param slice_start: Starting index of a slice
    :param slice_end: Ending index of a slice
    """
    url = f"http://{request.host}{BASE_PATH}/data/{id}?referenceName={referenceName}&start={slice_start}&end={slice_end}"
    arr.append({'url': url, })


def _create_slices(chunk_size, id, referenceName, start, end):
    """
    Returns array of slices of URLs

    :param chunk_size: The size of the chunk or slice
                      ( e.g. 10,000,000 pieces of data )
    :param id: ID of the file
    :param referenceName: Chromosome Number
    :param start: Desired starting index of a file
    :param end: Desired ending index of a file
    """
    urls = []
    chunks = int((end - start)/chunk_size)
    slice_start = start
    slice_end = 0
    if chunks >= 1 and start is not None and end is not None:
        for i in range(chunks):
            slice_end = slice_start + chunk_size
            _create_slice(urls, id, referenceName, slice_start, slice_end)
            slice_start = slice_end
        _create_slice(urls, id, referenceName, slice_start, end)
    else:  # One slice only
        url = f"http://{request.host}{BASE_PATH}/data/{id}"
        if referenceName and start and end:
            url += f"?referenceName={referenceName}&start={start}&end={end}"
        urls.append({"url": url})

    return urls


# Endpoints
def get_reads(id, referenceName=None, start=None, end=None):
    """
    Return URIs of reads:

    :param id: id of the file ( e.g. id=HG02102 for file HG02102.vcf.gz )
    :param referenceName: Chromesome Number
    :param start: Index of file to begin at
    :param end: Index of file to end at
    """
    if end is not None and end < start:
        response = {
            "detail": "End index cannot be less than start index",
            "status": 400,
            "title": "Bad Request",
            "type": "about:blank"
        }
        return "end cannot be less than start", 400

    if referenceName == "None":
        referenceName = None

    obj = {}
    if FILE_RETRIEVAL == "db":
        obj = _get_urls("db", "read", id, referenceName, start, end)
    elif FILE_RETRIEVAL == "minio":
        obj = _get_urls("minio", "read", id, referenceName, start, end)

    response = obj["response"]
    http_status_code = obj["http_status_code"]
    return response, http_status_code


def get_variants(id, referenceName=None, start=None, end=None):
    """
    Return URIs of variants:

    :param id: id of the file ( e.g. id=HG02102 for file HG02102.vcf.gz )
    :param referenceName: Chromesome Number
    :param start: Index of file to begin at
    :param end: Index of file to end at
    """
    if end is not None and end < start:
        response = {
            "detail": "End index cannot be smaller than start index",
            "status": 400,
            "title": "Bad Request",
            "type": "about:blank"
        }
        return "end cannot be less than start", 400

    if referenceName == "None":
        referenceName = None

    obj = {}
    if FILE_RETRIEVAL == "db":
        obj = _get_urls("db", "variant", id, referenceName, start, end)
    elif FILE_RETRIEVAL == "minio":
        obj = _get_urls("minio", "variant", id, referenceName, start, end)

    response = obj["response"]
    http_status_code = obj["http_status_code"]
    return response, http_status_code


def get_data(id, referenceName=None, format="bam", start=None, end=None):
    # start = 17148269, end = 17157211, referenceName = 21
    """
    Returns the specified variant or read file:

    :param id: id of the file ( e.g. id=HG02102 for file HG02102.vcf.gz )
    :param referenceName: Chromesome Number
    :param format: Format of output ( e.g bam, sam)
    :param start: Index of file to begin at
    :param end: Index of file to end at
    """
    if end is not None and end < start:
        response = {
            "detail": "End index cannot be smaller than start index",
            "status": 400,
            "title": "Bad Request",
            "type": "about:blank"
        }
        return "end cannot be less than start", 400

    if referenceName == "None":
        referenceName = None

    if format not in ["bam", "sam"]:
        return "Invalid format.", 400

    file_name = ""
    file_format = ""
    file_in_path = ""

    if FILE_RETRIEVAL == "db":
        file = _get_file_by_id(id)
        file_extension = file[0][1]
        file_format = file[0][2]
        file_name = f"{id}{file_extension}"
        file_in_path = f"{LOCAL_FILES_PATH}/{file_name}"
    elif FILE_RETRIEVAL == "minio":
        drs_objects = search_drs(id)
        file_format = _get_file_format_drs(drs_objects)
        main_file, index_file = _download_minio_file(drs_objects)

    # Write slice to temporary file
    ntf = NamedTemporaryFile(prefix='htsget', suffix='',
                             dir=TEMPORARY_FILES_PATH, mode='wb', delete=False)

    file_in = None
    file_out = None

    if file_format == "VCF" or file_format == "BCF":  # Variants
        if FILE_RETRIEVAL == "db":
            file_in = VariantFile(file_in_path)
        elif FILE_RETRIEVAL == "minio":
            file_in = VariantFile(
                main_file,
                index_filename=index_file
            )

            # TODO: leaving this here, works but may not be efficient to read from DRS directly
            #file_in = VariantFile(
            #    drs_objects['file']['access_methods'][0]['access_url']['url'],
            #    index_filename=drs_objects['index_file']['access_methods'][0]['access_url']['url']
            #)

        file_out = VariantFile(ntf.name, 'w', header=file_in.header)
    elif file_format == "BAM" or file_format == "CRAM":  # Reads

        if FILE_RETRIEVAL == "db":
            file_in = AlignmentFile(file_in_path)
        elif FILE_RETRIEVAL == "minio":
            file_in = AlignmentFile(
                main_file,
                index_filename=index_file
            )

        if format == "sam":
            output_format = "w"
        else:
            output_format = "wb"

        file_out = AlignmentFile(ntf.name, output_format, header=file_in.header)

    try:
        fetch = file_in.fetch(contig=referenceName, start=start, end=end)
    except ValueError:
        referenceName = referenceName.lower().replace("chr", "").upper()
        fetch = file_in.fetch(contig=referenceName, start=start, end=end)

    for rec in fetch:
        file_out.write(rec)

    file_in.close()
    file_out.close()

    # Send the temporary file as the response
    response = send_file(filename_or_fp=ntf.name,
                         attachment_filename=file_name, as_attachment=True)
    response.headers["x-filename"] = file_name
    response.headers["Access-Control-Expose-Headers"] = 'x-filename'
    os.remove(ntf.name)
    return response, 200


def _get_urls(file_retrieval, file_type, id, referenceName=None, start=None, end=None):
    """
    Searches for file from local sqlite db or minio from ID and Return URLS for Read/Variant

    :param file_retrieval: "minio" or "db"
    :param file_type: "read" or "variant"
    :param id: ID of a file
    :param referenceName: Chromosome Number
    :param start: Desired starting index of the file
    :param end: Desired ending index of the file
    """
    if file_type not in ["variant", "read"]:
        raise ValueError("File type must be 'variant' or 'read'")

    err_msg = f"No {file_type} found for id: {id}, try using the other endpoint"
    not_found_error = {"response": err_msg, "http_status_code": 404}

    file = ""
    file_exists = False
    if file_retrieval == "db":
        file = _get_file_by_id(id)  # returns an array of tuples
        file_exists = len(file) != 0
    elif file_retrieval == "minio":
        drs_objects = search_drs(id)

        if drs_objects:
            file_exists = True
    else:
        raise ValueError("file retrieval must be 'db' or 'minio'")

    if file_exists:
        file_format = ""
        file_path = ""
        if file_retrieval == "db":
            file_name = file[0][0] + file[0][1]
            file_format = file[0][2]
            file_path = f"{LOCAL_FILES_PATH}/{file_name}"
        elif file_retrieval == "minio":
            file_format = _get_file_format_drs(drs_objects)
            file_path = drs_objects

        if file_format == "VCF" or file_format == "BCF":
            if file_type != "variant":
                return not_found_error
        elif file_format == "BAM" or file_format == "CRAM":
            if file_type != "read":
                return not_found_error

        if start is None:
            start = _get_index(file_retrieval, "start", file_path, file_type)
        if end is None:
            end = _get_index(file_retrieval, "end", file_path, file_type)

        urls = _create_slices(CHUNK_SIZE, id, referenceName, start, end)
        response = {
            'htsget': {
                'format': file_format,
                'urls': urls
            }
        }
        return {"response": response, "http_status_code": 200}
    else:
        return not_found_error


def _get_index(file_retrieval, position, file_path, file_type):
    """
    Get the first or last index of a reads or variant file.
    File must be stored locally or on minio s3 bucket

    :param position: Get either first or last index.
        Options: first - "start"
                 last - "end"
    :param file_path: path of file
    :param file_type: Read or Variant
    """
    position = position.lower()
    if position not in ["start", "end"]:
        return "That position is not available"

    file_type = file_type.lower()
    if file_type not in ["variant", "read"]:
        return "That format is not available"

    file_in = 0
    if file_retrieval == "db":
        if file_type == "variant":
            file_in = VariantFile(file_path, "r")
        elif file_type == "read":
            file_in = AlignmentFile(file_path, "r")
    elif file_retrieval == "minio":
        main_file, index_file = _download_minio_file(file_path)

        if file_type == "variant":
            file_in = VariantFile(
                main_file,
                index_filename=index_file
            )
        elif file_type == "read":
            file_in = AlignmentFile(
                main_file,
                index_filename=index_file
            )

    # get the required index
    if position == "start":
        start = 0
        for rec in file_in.fetch():
            start = rec.pos
            break
        return start
    elif position == "end":
        end = 0
        for rec in file_in.fetch():
            end = rec.pos
        return end

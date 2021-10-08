from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,BucketAlreadyExists)
from pysam import VariantFile
import json
import sys
import io
import zlib
import subprocess

# Initialize minioClient with an endpoint and access/secret keys.
minioClient = Minio('play.min.io:9000',
                    access_key='Q3AM3UQ867SPQQA43P2F',
                    secret_key='zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG',
                    secure=True)

def create_bucket():
    # Make a bucket with the make_bucket API call.
    try:
        minioClient.make_bucket("miniotest", location="us-east-1")
        print("made bucket")
    except BucketAlreadyOwnedByYou as err:
        print("bucket owned")
        pass
    except BucketAlreadyExists as err:
        print("Bucket already exists")
        pass
    except ResponseError as err:
        raise
    else:
            # Put an object 'pumaserver_debug.log' with contents from 'pumaserver_debug.log'.
            print("else statement")
            try:
                minioClient.fput_object('maylogs', 'pumaserver_debug.log', '/tmp/pumaserver_debug.log')
            except ResponseError as err:
                print(err)

def upload_file():
    try:
        minioClient.fput_object('test', 'NA18537.vcf.gz', '../../data/files/NA18537.vcf.gz')
    except ResponseError as err:
        print(err)

def download_file():
    try:
        data = minioClient.fget_object('test', 'NA18537.vcf.gz.tbi', '../data/files/test.vcf.gz')
        print(data.object_name)
    except ResponseError as err:
        print(err)

def stream_gzip_decompress(stream):
    dec = zlib.decompressobj(32 + zlib.MAX_WBITS)  # offset 32 to skip the header
    for chunk in stream:
        rv = dec.decompress(chunk)
        if rv:
            yield rv

def download_file_2():
    try:
        data = minioClient.get_object('test', 'NA18537.vcf.gz')
        # vcf_buffer = VariantFile('-', 'w')
        f = open("../../data/files/NA18537.vcf.gz", "rb")
        # print(f.fileno())
        # content = f.read()
        # vcf = vcf_buffer.write(content)
        args =["echo", data.read()]

        with subprocess.Popen(args, stdout=subprocess.PIPE) as proc:
            fd_child = proc.stdout.fileno()
            print(fd_child)

            # with VariantFile(fd_child, "rb") as sam:
            #     for rec in sam:
            #         print(rec)
        # raw.raw.name = "-"
        # raw = io.FileIO(bytes.hex(data.read()), 'r')
        # mc_stream = data.stream()
        # mc_obj = data.read()

        # print(type(mc_stream))
        # print(type(mc_obj))
        # print(type(f))
        # print(type(raw))
        # print(f)
        # print(raw)
        # print(raw.readline())

        # raw.name = "name"
        # print(raw)
        # raw = data.read()
        # print(raw)

        # vcf = VariantFile(raw.fileno(), 'rb')


        # contents = f.read()
        # print()
        # f = io.BytesIO(data.read())
        # print(f)
        # vcf = VariantFile(raw)
        # print(vcf.header)
        # for rec in vcf.fetch():
        #     print(rec.pos)
        # infile = VariantFile("-", "r")
        # for s in infile:
        #     print(s)
    except ResponseError as err:
        print(err)


# download_file()P
# upload_file()
# download_file_2()
def test():
    test = "s3://Q3AM3UQ867SPQQA43P2F:zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG@play.min.io:9000/test/NA18537.vcf.gz"
    test2 = "s3://default@play/testfiles/NA18537.vcf.gz"
    vcf = VariantFile(test2)
    for rec in vcf.fetch():
        print(rec.pos)

# download_file_2()
test()

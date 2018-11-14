#!/usr/bin/env python3

from ga4gh.dos.client import Client
import htsget
from datetime import datetime, timezone

# https://stackoverflow.com/questions/8556398/generate-rfc-3339-timestamp-in-python#8556555
local_time = datetime.now(timezone.utc).astimezone()

# htsget docs - https://htsget.readthedocs.io/en/latest/quickstart.html
url = "http://htsnexus.rnd.dnanex.us/v1/reads/BroadHiSeqX_b37/NA12878"
with open("NA12878_2.bam", "wb") as output:
    htsget.get(url, output, reference_name="2", start=1000, end=20000)

# https://github.com/ga4gh/data-repository-service-schemas/blob/master/python/examples/object-type-examples.ipynb
client = Client("http://localhost:8080/ga4gh/dos/v1")
c = client.client
models = client.models

DataObject = models.get_model('DataObject')
Checksum = models.get_model('Checksum')
URL = models.get_model('URL')

na12878_2 = DataObject()
na12878_2.id = 'na12878_2'
na12878_2.name = 'NA12878_2.bam'
na12878_2.checksums = [
    Checksum(checksum='eaf80af5e9e54db5936578bed06ffcdc', type='md5')]
na12878_2.urls = [
    URL(
        url="http://htsnexus.rnd.dnanex.us/v1/reads/BroadHiSeqX_b37/NA12878",
        system_metadata={'reference_name': 2, 'start': 1000, 'end': 20000})]
na12878_2.aliases = ['NA12878 chr 2 subset']
na12878_2.size = '555749'
na12878_2.created = local_time

c.CreateDataObject(body={'data_object': na12878_2}).result()

c.GetDataObject(data_object_id='na12878_2').result()

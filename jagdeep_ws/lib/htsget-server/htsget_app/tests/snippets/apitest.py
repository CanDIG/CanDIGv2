import requests
from ast import literal_eval
from ga4gh.dos.client import Client
from datetime import datetime, timezone
import pytz

# https://stackoverflow.com/questions/8556398/generate-rfc-3339-timestamp-in-python#8556555
local_time = datetime.now(timezone.utc).astimezone()

# htsget docs - https://htsget.readthedocs.io/en/latest/quickstart.html

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
       system_metadata={'referenceName': 2, 'start': 1000, 'end': 20000})]
na12878_2.aliases = ['NA12878 chr 2 subset']
na12878_2.size = '555749'
na12878_2.created = local_time

c.CreateDataObject(body={'data_object': na12878_2}).result()

response = c.GetDataObject(data_object_id='na12878_2').result()

print(response)
# response = c.GetDataObject(data_object_id='NA18537').result()

# print(response['data_object']["name"])
# print(response['data_object']["urls"][0]['url'])

# response = c.GetDataObject(data_object_id='na12878_5')
# try:
#     print(response.result())
# except:
#     print('hello')
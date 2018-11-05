# CanDIG v2 PoC
- - -

## `mc` Client Examples

```bash

# Example - Minio Cloud Storage
mc config host add minio http://192.168.1.51 BKIKJAA5BMMU2RHO6IBB V7f1CwQqAcwo80UEIJEjc5gVQUSSx5ohQ9GSrr12

# Example - Amazon S3 Cloud Storage
mc config host add s3 https://s3.amazonaws.com BKIKJAA5BMMU2RHO6IBB V7f1CwQqAcwo80UEIJEjc5gVQUSSx5ohQ9GSrr12

```

## Data Repository Service Schemas

```bash

wget http://hgdownload.cse.ucsc.edu/goldenPath/hg38/chromosomes/chr22.fa.gz

md5sum chr22.fa.gz

# 41b47ce1cc21b558409c19b892e1c0d1  chr22.fa.gz

curl -X POST -H 'Content-Type: application/json' \
  --data '{"data_object":
          {"id": "hg38-chr22",
           "name": "Human Reference Chromosome 22",
           "checksums": [{"checksum": "41b47ce1cc21b558409c19b892e1c0d1", "type": "md5"}],
           "urls": [{"url": "http://hgdownload.cse.ucsc.edu/goldenPath/hg38/chromosomes/chr22.fa.gz"}],
           "size": "12255678"}}' http://localhost:8080/ga4gh/dos/v1/dataobjects

# We can then get the newly created Data Object by id
curl http://localhost:8080/ga4gh/dos/v1/dataobjects/hg38-chr22

# Or by checksum!
curl -X GET http://localhost:8080/ga4gh/dos/v1/dataobjects -d checksum=41b47ce1cc21b558409c19b892e1c0d1

```
## References

[Minio Client Quickstart]: (https://docs.minio.io/docs/minio-client-quickstart-guide#add-a-cloud-storage-service)
[GA4GH DRS Schemas]: (https://github.com/ga4gh/data-repository-service-schemas)
[GA4GH DOS Server Quickstart]: (https://data-object-service.readthedocs.io/en/latest/quickstart.html)

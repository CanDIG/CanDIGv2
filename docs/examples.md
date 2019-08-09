# Notes/Examples for Services
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

## HTSGET Client/Server Tools

![HTSNexus Core Mechanics Diagram](https://raw.githubusercontent.com/wiki/dnanexus-rnd/htsnexus/htsnexus_core_mechanic.png)

The htsnexus client tool simply emits BAM/CRAM/VCF to standard output, which can be redirected to a file or piped into samtools/bcftools. It delivers a well-formed BAM/CRAM/VCF file, with the proper header, even when slicing a genomic range. Here are the data accessions currently available:

| namespace | accession | format |
| --- | --- | --- |
| **platinum** <br/> Illumina Platinum Genomes stored at EBI | NA12877 NA12878 NA12879 NA12881 NA12882 NA12883 NA12884 NA12885 NA12886 NA12887 NA12888 NA12889 NA12890 NA12891 NA12892 NA12893 | BAM |
| **ENCODE** <br/> ChIP-seq data released by the ENCODE DCC in Jan 2016 | ENCFF014ABI ENCFF024MPE ENCFF070QUN ENCFF090MZL ENCFF124VCI ENCFF137WND ENCFF180VYU ENCFF308BKD ENCFF373VCV ENCFF465GPJ ENCFF572JRO ENCFF630NYB ENCFF743FRI ENCFF800DAY ENCFF862PIC ENCFF866OLR ENCFF904PIO ENCFF929AIJ ENCFF946BKE ENCFF951SEJ | BAM |
| **lh3bamsvr** <br/> Heng's examples | EXA00001 EXA00002 | BAM |
| **1000genomes_low_coverage** <br/> Low-coverage whole-genome sequencing from the 1000 Genomes Project | <a href="http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/phase3/data/">2,535 individual accessions</a> (example usage above) | BAM, CRAM |
| **1000genomes** <br/> 1000 Genomes Project variant calls | 20130502_autosomes | VCF

## `htnexus.py` Client Examples

```bash

# Download an ENCODE ChIP-Seq BAM
htsnexus ENCODE ENCFF904PIO > ENCFF904PIO.bam

# Slice a genomic range out of a Platinum Genomes BAM
htsnexus -r chr12:111766922-111817529 platinum NA12878 > NA12878_ALDH2.bam

# Count reads on chr21 in a 1000 Genomes BAM
htsnexus -r 21 1000genomes_low_coverage NA20276 | samtools view -c -

# id. with CRAM (samtools 1.2+ needed)
htsnexus -r 21 1000genomes_low_coverage HG01102 CRAM | samtools view -c -

# Stream reads from Heng Li's bamsvr and display as headered SAM
htsnexus -r 11:10899000-10900000 lh3bamsvr EXA00001 | samtools view -h - | less -S

# Slice a bgzipped VCF
htsnexus -r 12:112204691-112247789 1000genomes 20130502_autosomes vcf | gzip -dc | grep rs671 | cut -f1-16

```

### Use `htsnexus` to slice genomic range

```bash

$ ./htsnexus -v -r chr12:111766922-111817529 platinum NA12878 | wc -c
Query URL: http://htsnexus.rnd.dnanex.us/v1/reads/platinum/NA12878?format=BAM&referenceName=chr12&start=111766922&end=111817529
Response: {
  "urls": [
    {
      "url": "data:application/octet-stream;base64,[704 base64 characters]"
    },
    {
      "url": "https://dl.dnanex.us/F/D/8P6zFPZ0fy5z20bJzy32jbG4165F54Fv5fZFbzpK/NA12878_S1.bam",
      "headers": {
        "range": "bytes=81272945657-81275405960",
        "referer": "http://htsnexus.rnd.dnanex.us/v1/reads/platinum/NA12878?format=BAM&referenceName=chr12&start=111766922&end=111817529"
      }
    },
    {
      "url": "data:application/octet-stream;base64,[40 base64 characters]"
    }
  ],
  "namespace": "platinum",
  "accession": "NA12878",
  "reference": "hg19",
  "format": "BAM"
}
Piping: ['curl', '-LSs', '-H', 'range: bytes=81272945657-81275405960', '-H', 'referer: http://htsnexus.rnd.dnanex.us/v1/reads/platinum/NA12878?format=BAM&referenceName=chr12&start=111766922&end=111817529', 'https://dl.dnanex.us/F/D/8P6zFPZ0fy5z20bJzy32jbG4165F54Fv5fZFbzpK/NA12878_S1.bam']
Success
2460858

```

## References

* [Minio Client Quickstart](https://docs.minio.io/docs/minio-client-quickstart-guide#add-a-cloud-storage-service)
* [GA4GH DRS Schemas](https://github.com/ga4gh/data-repository-service-schemas)
* [GA4GH DOS Server Quickstart](https://data-object-service.readthedocs.io/en/latest/quickstart.html)
* [HTSNexus](https://github.com/dnanexus-rnd/htsnexus)

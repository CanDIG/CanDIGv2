/usr/bin/env bash

set -xe

pushd /root

## Download an ENCODE ChIP-Seq BAM
#htsnexus ENCODE ENCFF904PIO > ENCFF904PIO.bam

## Slice a genomic range out of a Platinum Genomes BAM
#htsnexus -r chr12:111766922-111817529 platinum NA12878 > NA12878_ALDH2.bam

## Count reads on chr21 in a 1000 Genomes BAM
#htsnexus -r 21 1000genomes_low_coverage NA20276 | samtools view -c -

## id. with CRAM (samtools 1.2+ needed)
#htsnexus -r 21 1000genomes_low_coverage HG01102 CRAM | samtools view -c -

## Stream reads from Heng Li's bamsvr and display as headered SAM
#htsnexus -r 11:10899000-10900000 lh3bamsvr EXA00001 | samtools view -h - | less -S

## Slice a bgzipped VCF
#htsnexus -r 12:112204691-112247789 1000genomes 20130502_autosomes vcf | gzip -dc | grep rs671 | cut -f1-16

curl -LO https://s3.amazonaws.com/1000genomes/phase3/data/NA20276/alignment/NA20276.mapped.ILLUMINA.bwa.ASW.low_coverage.20120522.bam

/root/htsnexus/indexer/htsnexus_index_bam /root/htsnexus/server/test/test.sql 1000genomes_low_coverage NA20276 /root/NA20276.mapped.ILLUMINA.bwa.ASW.low_coverage.20120522.bam http://ga4gh-dos:8080/ga4gh/dos/v1/dataobjects/1000genomes-NA20276

popd

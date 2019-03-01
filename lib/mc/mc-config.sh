#! /usr/bin/env bash

set -xe

mc config host add minio http://minio:9000 <(/run/secrets/access_key) <(/run/secrets/secret_key)

wget https://s3.amazonaws.com/1000genomes/phase3/data/NA20276/alignment/NA20276.mapped.ILLUMINA.bwa.ASW.low_coverage.20120522.bam

mc mb minio/candig/
mc mb minio/candig/1000genomes/phase3/data/NA20276/alignment/
mc cp NA20276.mapped.ILLUMINA.bwa.ASW.low_coverage.20120522.bam minio/candig/1000genomes/phase3/data/NA20276/alignment/

#!/usr/bin/env bash

set -xe

## Preliminaries
# Set a number of shell variables, to make what follows easier to read.
BASE="$PWD/exome-case-study"
BIN_VERSION="0.7.2"
MODEL_VERSION="0.7.2"
MODEL_NAME="DeepVariant-inception_v3-${MODEL_VERSION}+data-wes_standard"
MODEL_HTTP_DIR="https://storage.googleapis.com/deepvariant/models/DeepVariant/${MODEL_VERSION}/${MODEL_NAME}"

INPUT_DIR="${BASE}/input"
MODELS_DIR="${INPUT_DIR}/models"
MODEL="${MODELS_DIR}/model.ckpt"
DATA_DIR="${INPUT_DIR}/data"
#REF="${DATA_DIR}/hs37d5.fa.gz"
#BAM="${DATA_DIR}/151002_7001448_0359_AC7F6GANXX_Sample_HG002-EEogPU_v02-KIT-Av5_AGATGTAC_L008.posiSrt.markDup.bam"
#TRUTH_VCF="${DATA_DIR}/HG002_GRCh37_GIAB_highconf_CG-IllFB-IllGATKHC-Ion-10X-SOLID_CHROM1-22_v.3.3.2_highconf_triophased.vcf.gz"
#TRUTH_BED="${DATA_DIR}/HG002_GRCh37_GIAB_highconf_CG-IllFB-IllGATKHC-Ion-10X-SOLID_CHROM1-22_v.3.3.2_highconf_noinconsistent.bed"

REF="${DATA_DIR}/ucsc.hg19.chr20.unittest.fasta.gz"
BAM="${DATA_DIR}/NA12878_S1.chr20.10_10p1mb.bam"
BAI="${DATA_DIR}/NA12878_S1.chr20.10_10p1mb.bai"

N_SHARDS="64"

OUTPUT_DIR="${BASE}/output"
EXAMPLES="${OUTPUT_DIR}/HG002.examples.tfrecord@${N_SHARDS}.gz"
GVCF_TFRECORDS="${OUTPUT_DIR}/HG002.gvcf.tfrecord@${N_SHARDS}.gz"
CALL_VARIANTS_OUTPUT="${OUTPUT_DIR}/HG002.cvo.tfrecord.gz"
OUTPUT_VCF="${OUTPUT_DIR}/HG002.output.vcf.gz"
OUTPUT_GVCF="${OUTPUT_DIR}/HG002.output.g.vcf.gz"
LOG_DIR="${OUTPUT_DIR}/logs"

CAPTURE_BED="${DATA_DIR}/agilent_sureselect_human_all_exon_v5_b37_targets.bed"

## Create local directory structure
mkdir -p "${OUTPUT_DIR}"
mkdir -p "${DATA_DIR}"
mkdir -p "${MODELS_DIR}"
mkdir -p "${LOG_DIR}"

## Download models, and test data
# Copy the model files to your local disk.
aria2c -c -x10 -s10 -d "${MODELS_DIR}" "${MODEL_HTTP_DIR}"/model.ckpt.data-00000-of-00001
aria2c -c -x10 -s10 -d "${MODELS_DIR}" "${MODEL_HTTP_DIR}"/model.ckpt.index
aria2c -c -x10 -s10 -d "${MODELS_DIR}" "${MODEL_HTTP_DIR}"/model.ckpt.meta

# Copy the data
aria2c -c -x10 -s10 -d "${DATA_DIR}" https://storage.googleapis.com/deepvariant/exome-case-study-testdata/151002_7001448_0359_AC7F6GANXX_Sample_HG002-EEogPU_v02-KIT-Av5_AGATGTAC_L008.posiSrt.markDup.bai
aria2c -c -x10 -s10 -d "${DATA_DIR}" https://storage.googleapis.com/deepvariant/exome-case-study-testdata/151002_7001448_0359_AC7F6GANXX_Sample_HG002-EEogPU_v02-KIT-Av5_AGATGTAC_L008.posiSrt.markDup.bam
aria2c -c -x10 -s10 -d "${DATA_DIR}" https://storage.googleapis.com/deepvariant/exome-case-study-testdata/HG002_GRCh37_GIAB_highconf_CG-IllFB-IllGATKHC-Ion-10X-SOLID_CHROM1-22_v.3.3.2_highconf_noinconsistent.bed
aria2c -c -x10 -s10 -d "${DATA_DIR}" https://storage.googleapis.com/deepvariant/exome-case-study-testdata/HG002_GRCh37_GIAB_highconf_CG-IllFB-IllGATKHC-Ion-10X-SOLID_CHROM1-22_v.3.3.2_highconf_triophased.vcf.gz
aria2c -c -x10 -s10 -d "${DATA_DIR}" https://storage.googleapis.com/deepvariant/exome-case-study-testdata/HG002_GRCh37_GIAB_highconf_CG-IllFB-IllGATKHC-Ion-10X-SOLID_CHROM1-22_v.3.3.2_highconf_triophased.vcf.gz.tbi
aria2c -c -x10 -s10 -d "${DATA_DIR}" https://storage.googleapis.com/deepvariant/exome-case-study-testdata/agilent_sureselect_human_all_exon_v5_b37_targets.bed
aria2c -c -x10 -s10 -d "${DATA_DIR}" https://storage.googleapis.com/deepvariant/exome-case-study-testdata/hs37d5.fa.gz
aria2c -c -x10 -s10 -d "${DATA_DIR}" https://storage.googleapis.com/deepvariant/exome-case-study-testdata/hs37d5.fa.gz.fai
aria2c -c -x10 -s10 -d "${DATA_DIR}" https://storage.googleapis.com/deepvariant/exome-case-study-testdata/hs37d5.fa.gz.gzi
aria2c -c -x10 -s10 -d "${DATA_DIR}" https://storage.googleapis.com/deepvariant/exome-case-study-testdata/hs37d5.fa.gzi

wget -P "${DATA_DIR}" "${DATA_HTTP_DIR}"/NA12878_S1.chr20.10_10p1mb.bam
wget -P "${DATA_DIR}" "${DATA_HTTP_DIR}"/NA12878_S1.chr20.10_10p1mb.bam.bai
wget -P "${DATA_DIR}" "${DATA_HTTP_DIR}"/test_nist.b37_chr20_100kbp_at_10mb.bed
wget -P "${DATA_DIR}" "${DATA_HTTP_DIR}"/test_nist.b37_chr20_100kbp_at_10mb.vcf.gz
wget -P "${DATA_DIR}" "${DATA_HTTP_DIR}"/test_nist.b37_chr20_100kbp_at_10mb.vcf.gz.tbi
wget -P "${DATA_DIR}" "${DATA_HTTP_DIR}"/ucsc.hg19.chr20.unittest.fasta
wget -P "${DATA_DIR}" "${DATA_HTTP_DIR}"/ucsc.hg19.chr20.unittest.fasta.fai
wget -P "${DATA_DIR}" "${DATA_HTTP_DIR}"/ucsc.hg19.chr20.unittest.fasta.gz
wget -P "${DATA_DIR}" "${DATA_HTTP_DIR}"/ucsc.hg19.chr20.unittest.fasta.gz.fai
wget -P "${DATA_DIR}" "${DATA_HTTP_DIR}"/ucsc.hg19.chr20.unittest.fasta.gz.gzi

#git clone https://github.com/dnanexus-rnd/DeepVariant-GLnexus-WDL.git

cat > htsget_DeepVariant_inputs.json << EOF
{
  "htsget_DeepVariant.htsget_format": "VCF",
  "htsget_DeepVariant.ref_fasta_gz": "${REF}",
  "htsget_DeepVariant.ranges": ["chr12:111766922-111817529"],
  "htsget_DeepVariant.model_tar": "${MODEL}",
  "htsget_DeepVariant.deepvariant_docker": "gcr.io/deepvariant-docker/deepvariant:${BIN_VERSION}",
  "htsget_DeepVariant.accession": "NA12878",
  "htsget_DeepVariant.htsget_endpoint": "https://htsnexus.rnd.dnanex.us/v1/reads/BroadHiSeqX_b37"
}
EOF

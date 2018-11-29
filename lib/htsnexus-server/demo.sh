/usr/bin/env sh

set -xe

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

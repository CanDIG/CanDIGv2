from pysam import VariantFile, AlignmentFile
from tempfile import NamedTemporaryFile


def parse_variant():
    vcf_in = VariantFile('../../data/files/NA18537.vcf.gz')
    for rec in vcf_in.fetch("21", 10144, 42210200):
        print(rec.chrom)


def parse_read():
    bam_in = AlignmentFile("./files/NA02102.bam", "rb")
    for x in bam_in.fetch("chr4", 10144, 10200):
        print(x)


def compare_files():
    file_one = VariantFile('../../data/files/NA18537.vcf.gz')
    file_two = VariantFile('../../data/files/NA18537.vcf.gz')
    for x, y in zip(file_one.fetch(), file_two.fetch()):
        print(x == y)


def test():
    f = VariantFile('../../data/files/NA18537.vcf.gz')
    for rec in f.fetch():
        print(rec.chrom)

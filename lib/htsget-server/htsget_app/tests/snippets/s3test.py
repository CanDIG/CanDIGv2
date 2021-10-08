from pysam import VariantFile

s3_path = "s3://default@play/testfiles/NA18537.vcf.gz"
vcf_in = VariantFile(s3_path)
for rec in vcf_in.fetch():
    print(rec.pos)

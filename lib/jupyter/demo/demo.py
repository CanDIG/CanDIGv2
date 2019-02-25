#!/usr/bin/env python2

import htsget

url = "http://htsnexus.rnd.dnanex.us/v1/reads/BroadHiSeqX_b37/NA12878"
with open("NA12878_2.bam", "wb") as output:
    htsget.get(url, output, reference_name="2", start=1000, end=20000)

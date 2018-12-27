#!/usr/bin/env python2

import pandas as pd
import re
import os
from minio import Minio
from minio.error import ResponseError
from collections import Counter


# step 1: load file from object store
minioClient = Minio('localhost:9000',
                    access_key='admin',
                    secret_key='IjoEBEwSfUO2VtisyPv11A=',
                    secure=False)

# get a full object
try:
    data = minioClient.get_object('candig', 'origin_of_species.txt')

except ResponseError as err:
    print(err)

# stream data from object store in sections
wordlist = ''

for d in data.stream(32*1024):
    wordlist += d


# step 2: normalize data

# replace empty lines, punctuation, and special characters with space
# convert all words to lowercase
words = re.compile(r'\W+', re.UNICODE).split(wordlist.lower())
# print(sorted(words))

# step 3: save normalized, intermediate data

# df: dataframe
df = pd.Series(sorted(words))
# df = np.array(sorted(words))

# f: file
f = '/tmp/normalized.pkl'

df.to_pickle(f)

# fd: file descriptor
fd = os.stat(f)

try:
    with open(f, 'rb') as data:
        minioClient.put_object('candig', 'normalized.pkl',
                               data, fd.st_size,
                               content_type='application/pickle')

except ResponseError as err:
    print(err)


# step 4: create dictionary of words and frequencies
wordcount = Counter(df)

# quick statistic summary of your data
# print(wordcount.describe())


# step 5: output results
# print(wordcount)
# print(wordcount.index)
# print(wordcount.columns)
# print(wordcount.values)
# print(wordcount.sort_index(axis=1, ascending=False))
print(wordcount.most_common(10))

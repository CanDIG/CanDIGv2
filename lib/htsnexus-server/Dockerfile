FROM ubuntu:trusty
LABEL maintainer=CanDIG

WORKDIR /root

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  build-essential xz-utils curl ca-certificates python-pip pigz git cmake

# deps for indexer
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  zlib1g-dev libbz2-dev liblzma-dev libcurl4-openssl-dev sqlite3 libsqlite3-dev \
  libncurses5-dev libncursesw5-dev

RUN pip install --upgrade awscli requests

# fixes issue with autoheader package
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --reinstall autoconf

RUN git clone https://github.com/dnanexus-rnd/htsnexus.git

WORKDIR /root/htsnexus/indexer
RUN cmake . && make

WORKDIR /root/htsnexus/server
RUN make all test

WORKDIR /root/htsnexus
RUN cp client/htsnexus.py /usr/bin/htsnexus && \
  chmod 744 /usr/bin/htsnexus

RUN test/htsnexus_integration_tests.sh && \
  mv /tmp/htsnexus_integration_test.db htsnexus-server.db

#COPY demo.sh .
#RUN bash demo.sh

ENTRYPOINT ["$PWD/server/server.sh"]

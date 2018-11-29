FROM python:alpine
MAINTAINER CanDIG

WORKDIR /root

RUN apk update
RUN apk add nodejs npm
RUN apk add make xz curl ca-certificates pigz
RUN apk add git
RUN pip install awscli

RUN git clone https://github.com/dnanexus-rnd/htsnexus.git

COPY demo.sh .

WORKDIR /root/htsnexus

RUN cp client/htsnexus.py /usr/bin/htsnexus
RUN chmod 744 /usr/bin/htsnexus

WORKDIR /root/htsnexus/server

#RUN make all test

EXPOSE 48444

ENTRYPOINT ["server.sh"]

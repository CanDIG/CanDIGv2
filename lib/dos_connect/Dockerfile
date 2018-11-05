FROM alpine:latest
MAINTAINER CanDIG

WORKDIR /root

RUN apk add python py-pip git

RUN git clone git@github.com:ohsu-comp-bio/dos_connect.git

RUN pip install -r dos_connect/requirements.txt

RUN pip install -r dos_connect/server/requirements.txt

ENTRYPOINT ["ga4gh_dos_server"]

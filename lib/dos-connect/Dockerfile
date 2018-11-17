FROM python:alpine
MAINTAINER CanDIG

WORKDIR /root

RUN apk add git

RUN git clone git@github.com:ohsu-comp-bio/dos_connect.git

RUN pip install -r dos_connect/requirements.txt

RUN pip install -r dos_connect/server/requirements.txt


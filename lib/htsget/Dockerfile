FROM python:alpine
MAINTAINER CanDIG

ARG dos_version
ARG htsget_version

WORKDIR /root

#RUN apk add python py-pip

RUN pip install ga4gh-dos-schemas==$dos_version htsget==$htsget_version

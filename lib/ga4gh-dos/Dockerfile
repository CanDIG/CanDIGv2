FROM python:alpine
LABEL maintainer=CanDIG

ARG dos_version

WORKDIR /root

RUN apk update
#RUN apk add python py-pip git

RUN pip install ga4gh-dos-schemas==$dos_version

ENTRYPOINT ["ga4gh_dos_server"]

FROM alpine:latest
MAINTAINER CanDIG

WORKDIR /root

RUN apk add python py-pip git

RUN pip install ga4gh-dos-schemas==$dos_version

ENTRYPOINT ["ga4gh_dos_server"]

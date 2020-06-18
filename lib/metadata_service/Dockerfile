ARG venv_python

FROM python:${venv_python}-alpine

LABEL Maintainer="CanDIG Project"

USER root

RUN apk update

RUN apk add \
  autoconf \
  automake \
  make \
  gcc \
  linux-headers \
  perl \
  bash \
  build-base \
  musl-dev \
  zlib-dev \
  bzip2-dev \
  xz-dev \
  libcurl \
  curl \
  curl-dev \
  yaml-dev \
  libressl-dev \
  git

COPY metadata_service_v2 /app/metadata_service_v2
WORKDIR /app/metadata_service_v2

RUN pip install -r requirements.txt

ENTRYPOINT [ "./manage.py" ]

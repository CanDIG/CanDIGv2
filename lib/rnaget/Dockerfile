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
  git \
  openblas-dev \
  hdf5-dev

COPY rnaget_service /app/rnaget_service
WORKDIR /app/rnaget_service

RUN pip install -r requirements.txt && \
  pip install -r requirements_dev.txt && \
  python setup.py develop && \
  npm install -g dredd

 ENTRYPOINT ["candig_rnaget"]

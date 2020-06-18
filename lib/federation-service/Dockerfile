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

COPY federation_service /app/federation_service
WORKDIR /app/federation_service

RUN pip install -r requirements.txt

 ENTRYPOINT ["python", "-m", "candig_federation"]

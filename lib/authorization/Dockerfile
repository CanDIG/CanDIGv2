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
	libxml2-dev \
	libxml2

COPY candig_authz_service /app/candig_authz_service

WORKDIR /app/candig_authz_service

RUN pip install -r requirements.txt && \
	pip install git+https://github.com/candig/candig_authz_service.git

COPY access_list.tsv .

ENTRYPOINT ["candig_authz_service"]

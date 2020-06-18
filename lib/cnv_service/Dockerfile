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
	rust \
	cargo

COPY candig_cnv_service /app/candig_cnv_service
WORKDIR /app/candig_cnv_service

# TODO: fix build issue pyo3
RUN pip install setuptools-rust && \
	python setup.py install

ENTRYPOINT ["candig_cnv_service"]

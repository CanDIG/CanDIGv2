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


COPY datasets_service /app/datasets_service
WORKDIR /app/datasets_service

# TODO: fix build issue pyo3
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "-m", "candig_dataset_service" ]

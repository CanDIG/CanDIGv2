ARG venv_python

FROM python:${venv_python}-alpine

LABEL Maintainer="CanDIG Project"

USER root

RUN apk update

RUN apk add --no-cache \
	autoconf \
	automake \
	make \
	gcc \
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

COPY . /app/htsget_server

WORKDIR /app/htsget_server

RUN python setup.py install && pip install --no-cache-dir -U connexion

ENTRYPOINT ["python3", "htsget_server/server.py"]

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

RUN mkdir /app
WORKDIR /app

COPY chord_metadata_service /app/chord_metadata_service

WORKDIR /app/chord_metadata_service
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "manage.py", "runserver"]

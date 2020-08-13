ARG venv_python

FROM python:${venv_python}-alpine

LABEL Maintainer="CanDIG Project"

USER root

RUN apk update

RUN apk add --no-cache \
	autoconf \
	automake \
	bash \
	build-base \
	bzip2-dev \
	curl \
	curl-dev \
	gcc \
	git \
	libcurl \
	libressl-dev \
	linux-headers \
	make \
	musl-dev \
	perl \
	postgresql-dev \
	postgresql-libs \
	xz-dev \
	yaml-dev \
	zlib-dev

RUN mkdir /app
WORKDIR /app

COPY chord_metadata_service /app/chord_metadata_service

WORKDIR /app/chord_metadata_service
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "manage.py", "runserver"]

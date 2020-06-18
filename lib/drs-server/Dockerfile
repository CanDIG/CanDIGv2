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
	postgresql-dev \
	libffi-dev

COPY chord_drs /app/chord_drs
WORKDIR /app/chord_drs

RUN pip install -r requirements.txt && flask db upgrade

# Run the model service server
ENTRYPOINT ["flask", "run"]

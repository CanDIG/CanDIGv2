ARG venv_python
ARG alpine_version
FROM python:${venv_python}-alpine${alpine_version}

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
	git \
	rust \
	cargo \
	postgresql-dev \
	libffi-dev

COPY chord_drs /app/chord_drs
WORKDIR /app/chord_drs

RUN pip install --no-cache-dir -r requirements.txt && flask db upgrade

# Run the model service server
ENTRYPOINT ["flask", "run"]

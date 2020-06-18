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

# clone or COPY module repo as needed
# example:
# RUN git clone https://github.com/c3g/chord_drs.git
# COPY chord_drs /app/chord_drs

# run necessary steps to implement module
# example:
# WORKDIR /app/chord_drs
# RUN pip install -r requirements.txt && flask db upgrade

# Run the model service server
# example:
# ENTRYPOINT ["flask", "run"]

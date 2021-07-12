ARG venv_python

FROM python:${venv_python}-alpine${alpine_version}

LABEL Maintainer="CanDIG Project"

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on

RUN adduser -h /app -D user

RUN apk add --no-cache \
  autoconf \
  automake \
  build-base \
  bzip2-dev \
  curl \
  curl-dev \
  gcc \
  git \
  libcurl \
  libffi-dev \
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

USER user
WORKDIR /app

# clone or COPY module repo as needed
# example:
# RUN git clone https://github.com/c3g/chord_drs.git
# COPY chord_drs /app/chord_drs

# run necessary steps to implement module
# example:
# WORKDIR /app/chord_drs
# RUN pip install --no-cache-dir -r requirements.txt && flask db upgrade

# Run the model service server
# example:
# ENTRYPOINT ["flask", "run"]

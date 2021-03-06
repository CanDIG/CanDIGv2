ARG venv_python
ARG alpine_version
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
  bash \
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
  rust \
  cargo \
  postgresql-dev \
  postgresql-libs \
  xz-dev \
  yaml-dev \
  zlib-dev

USER user
WORKDIR /app

COPY chord_metadata_service /app/chord_metadata_service

WORKDIR /app/chord_metadata_service
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "manage.py", "runserver"]

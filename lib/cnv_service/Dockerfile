ARG venv_python

FROM python:${venv_python}-buster

LABEL Maintainer="CanDIG Project"

COPY candig_cnv_service /app/candig_cnv_service

WORKDIR /app/candig_cnv_service

RUN python setup.py install

ENTRYPOINT ["candig_cnv_service"]

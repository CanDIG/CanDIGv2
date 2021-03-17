ARG venv_python

FROM python:${venv_python}-slim

LABEL Maintainer="CanDIG Project"

RUN apt-get update && apt-get install -y build-essential

COPY candig_cnv_service /app/candig_cnv_service

WORKDIR /app/candig_cnv_service

#RUN python setup.py install
RUN pip install --no-cache-dir -e .

ENTRYPOINT ["candig_cnv_service"]

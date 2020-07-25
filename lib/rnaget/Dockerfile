ARG venv_python

FROM python:${venv_python}-buster

LABEL Maintainer="CanDIG Project"

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y npm

COPY rnaget_service /app/rnaget_service

WORKDIR /app/rnaget_service

RUN pip install -r requirements.txt && \
  pip install -r requirements_dev.txt && \
  python setup.py develop && \
  npm install -g dredd

 ENTRYPOINT ["candig_rnaget"]

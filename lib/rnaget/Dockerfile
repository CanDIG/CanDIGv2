ARG venv_python

FROM python:${venv_python}-slim

LABEL Maintainer="CanDIG Project"

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y npm

COPY rnaget_service /app/rnaget_service

WORKDIR /app/rnaget_service

RUN pip install --no-cache-dir -r requirements.txt && \
  pip install --no-cache-dir -r requirements_dev.txt && \
  python setup.py develop && \
  npm install -g dredd

 ENTRYPOINT ["candig_rnaget"]

ARG venv_python

FROM python:${venv_python}-slim

LABEL Maintainer="CanDIG Project"

COPY datasets_service /app/datasets_service

WORKDIR /app/datasets_service

RUN apt-get update
RUN apt-get -y install gcc libc-dev
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "-m", "candig_dataset_service" ]

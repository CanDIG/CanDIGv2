ARG venv_python

FROM python:${venv_python}-buster

LABEL Maintainer="CanDIG Project"

COPY datasets_service /app/datasets_service

WORKDIR /app/datasets_service

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "-m", "candig_dataset_service" ]

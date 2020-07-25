ARG venv_python

FROM python:${venv_python}-buster

LABEL Maintainer="CanDIG Project"

COPY metadata_service_v2 /app/metadata_service_v2

WORKDIR /app/metadata_service_v2

RUN pip install -r requirements.txt

ENTRYPOINT [ "./manage.py" ]

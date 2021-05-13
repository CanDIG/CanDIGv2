ARG venv_python

FROM python:${venv_python}-buster

LABEL Maintainer="CanDIG Project"

RUN mkdir -p /arbiter

COPY server.py /arbiter
COPY requirements.txt /arbiter

WORKDIR /arbiter

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "-u", "/arbiter/server.py"]

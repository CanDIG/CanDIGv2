ARG venv_python

FROM python:${venv_python}-buster

LABEL Maintainer="CanDIG Project"

RUN mkdir -p /app/candig-server-arbiter

COPY server.py /app/candig-server-arbiter
COPY requirements.txt /app/candig-server-arbiter

WORKDIR /app/candig-server-arbiter

RUN pip install -r requirements.txt
# RUN pip install candig-server==1.3.0 && pip install candig-ingest==1.3.1

# # Uncomment below lines if you want to ingest some mock data
# RUN mkdir candig-example-data && \
# 	wget https://raw.githubusercontent.com/CanDIG/candig-ingest/master/candig/ingest/mock_data/clinical_metadata_tier1.json && \
# 	wget https://raw.githubusercontent.com/CanDIG/candig-ingest/master/candig/ingest/mock_data/clinical_metadata_tier2.json && \
# 	ingest candig-example-data/registry.db mock1 clinical_metadata_tier1.json && \
# 	ingest candig-example-data/registry.db mock2 clinical_metadata_tier2.json

RUN ls /app
RUN ls /app/candig-server-arbiter
#RUN ls /app

ENTRYPOINT ["python3", "-u", "/app/candig-server-arbiter/server.py"]

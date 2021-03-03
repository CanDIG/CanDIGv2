ARG venv_python

FROM python:${venv_python}-slim

LABEL Maintainer="CanDIG Project"

RUN mkdir -p /app/candig-server

WORKDIR /app/candig-server

RUN apt-get update && \
	apt-get install -y build-essential zlib1g-dev wget && \
	apt-get autoclean && \
	apt-get autoremove -y

RUN pip install candig-server && pip install candig-ingest==1.3.1

# Uncomment below lines if you want to ingest some mock data
RUN mkdir candig-example-data && \
	wget https://raw.githubusercontent.com/CanDIG/candig-ingest/master/candig/ingest/mock_data/clinical_metadata_tier1.json && \
	wget https://raw.githubusercontent.com/CanDIG/candig-ingest/master/candig/ingest/mock_data/clinical_metadata_tier2.json && \
	ingest candig-example-data/registry.db mock1 clinical_metadata_tier1.json && \
	ingest candig-example-data/registry.db mock2 clinical_metadata_tier2.json

ENTRYPOINT ["candig_server"]

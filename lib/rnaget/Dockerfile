FROM ghcr.io/bento-platform/bento_base_image:python-debian-2024.07.09

RUN apt-get update && apt-get install -y postgresql-client

RUN pip install --no-cache-dir "uvicorn[standard]==0.30.1"


WORKDIR /tds

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry config virtualenvs.create false && \
    poetry --no-cache install --without dev --no-root

COPY transcriptomics_data_service transcriptomics_data_service
COPY lib lib
COPY entrypoint.bash .
COPY run.bash .
COPY LICENSE .
COPY README.md .
COPY create_db.sh .

RUN poetry install --without dev

ENTRYPOINT [ "bash", "./entrypoint.bash" ]
CMD [ "bash", "./run.bash" ]
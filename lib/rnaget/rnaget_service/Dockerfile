FROM python:3-slim-stretch
LABEL Maintainer "CanDIG Project"

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt && \
    python setup.py install

EXPOSE 3000

# Run the RNAget service server
# provide some explicit defaults if no arguments are given
ENTRYPOINT [ "candig_rnaget", "--port", "3000"]
CMD [ "--logfile", "log/rnaget.log",\
      "--database", "data/rnaget.sqlite",\
      "--tmpdata", "data/tmp/" ]


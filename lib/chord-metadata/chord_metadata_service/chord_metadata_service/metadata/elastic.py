import logging
from elasticsearch import Elasticsearch


logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)

es = Elasticsearch()

if not es.ping():
    # Elasticsearch is considered an optional part of the application
    es = None

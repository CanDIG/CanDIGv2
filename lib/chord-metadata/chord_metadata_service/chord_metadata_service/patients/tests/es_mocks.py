from unittest.mock import Mock


INDEXING_SUCCESS = {
    '_index': 'fhir_metadata',
    '_type': '_doc',
    '_id': 'ind:NA19648',
    '_version': 1,
    'result': 'created',
    '_shards': {'total': 2, 'successful': 1, 'failed': 0},
    '_seq_no': 835,
    '_primary_term': 1
}

DELETE_DOC_SUCCESS = {
    '_index': 'fhir_metadata',
    '_type': '_doc',
    '_id': 'ind:HG00315',
    '_version': 3,
    'result': 'deleted',
    '_shards': {'total': 2, 'successful': 1, 'failed': 0},
    '_seq_no': 1769,
    '_primary_term': 1
}


# TODO: as it stands we can merely import this to mock any calls
# when testing, maybe a bit sketchy for a setup, could be error-prone
es = Mock()

es.index = Mock(return_value=INDEXING_SUCCESS)
es.delete = Mock(return_value=DELETE_DOC_SUCCESS)

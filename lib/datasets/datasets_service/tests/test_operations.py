"""
Test suite to unit test operations
"""

import uuid
import os
import sys
import pytest

sys.path.append("{}/{}".format(os.getcwd(), "candig_dataset_service"))
sys.path.append(os.getcwd())

from candig_dataset_service import orm
from candig_dataset_service.__main__ import app
from candig_dataset_service.api import operations
from tests.test_structs import *


@pytest.fixture(name='test_client')
def load_test_client(db_filename="operations.db"):  # pylint: disable=too-many-locals
    # delete db if already exists and close session
    try:
        orm.close_session()
        os.remove(db_filename)

    except FileNotFoundError:
        pass
    except OSError:
        raise

    context = app.app.app_context()

    with context:
        orm.init_db('sqlite:///' + db_filename)
        dataset_1, dataset_2, changelog_1, changelog_2 = load_test_objects()
        app.app.config['BASE_DL_URL'] = 'http://127.0.0.1'

    return dataset_1, dataset_2, context, changelog_1, changelog_2


def test_post_dataset_exists(test_client):
    """
    post_dataset
    """
    ds1, ds2, context, _, _ = test_client

    with context:
        _, code = operations.post_dataset({'id': ds1['id']})
        assert code == 405


def test_post_dataset_field_error(test_client):
    """
    post_dataset
    """
    ds1, ds2, context, _, _ = test_client

    with context:
        _, code = operations.post_dataset({'invalid': ds1['id']})
        assert code == 400


def test_post_dataset_key_error(test_client):
    """
    post_dataset
    """
    ds1, ds2, context, _, _ = test_client

    with context:
        _, code = operations.post_dataset({'id': 6547864725, 'version': 55})
        assert code == 500


def test_get_dataset_by_id(test_client):
    """
    get_dataset_by_id
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        result, code = operations.get_dataset_by_id(ds1['id'])
        assert result['id'] == uuid.UUID(ds1['id']).hex
        assert code == 200

        result, code = operations.get_dataset_by_id(ds2['id'])
        assert result['id'] == uuid.UUID(ds2['id']).hex
        assert code == 200


def test_get_dataset_ontologies(test_client):
    """
    get_dataset_by_id
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        result, code = operations.get_dataset_by_id(ds1['id'])
        assert result['ontologies'] == ontologies['d1']['terms']
        assert code == 200


def test_get_dataset_by_id_key_error(test_client):
    """
    get_dataset_by_id
    """

    ds1, _, context, _, _ = test_client

    with context:

        result, code = operations.get_dataset_by_id('Wrong')
        assert code == 404


def test_delete_dataset_by_id(test_client):
    """
    delete_dataset_by_id
    """

    _, ds2, context, _, _ = test_client

    with context:
        _, code = operations.delete_dataset_by_id(ds2['id'])
        assert code == 204

        result, code = operations.get_dataset_by_id(ds2['id'])
        assert code == 404


def test_delete_dataset_by_id_missing(test_client):
    """
    delete_dataset_by_id
    """

    _, ds2, context, _, _ = test_client

    with context:
        _, code = operations.delete_dataset_by_id(uuid.uuid1().hex)
        assert code == 404


def test_delete_dataset_by_id_bad_UUID(test_client):
    """
    delete_dataset_by_id
    """

    _, ds2, context, _, _ = test_client

    with context:
        _, code = operations.delete_dataset_by_id('wrong')
        assert code == 500
        _, code = operations.delete_dataset_by_id(564564)
        assert code == 500


def test_search_datasets_basic(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets()
        assert len(datasets) == 2
        assert datasets == [ds1, ds2]
        assert code == 200


def test_search_datasets_version_1(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets(version='0.1')
        assert len(datasets) == 1
        assert datasets == [ds1]
        assert code == 200


def test_search_datasets_version_2(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets(version='0.3')
        assert len(datasets) == 1
        assert datasets == [ds2]
        assert code == 200


def test_search_datasets_version_none(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets(version='0.22')
        assert len(datasets) == 0
        assert datasets == []
        assert code == 200


def test_search_datasets_tag_1(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets(tags=['test'])
        assert len(datasets) == 1
        assert datasets == [ds2]
        assert code == 200


def test_search_datasets_tag_2(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets(tags=['candig'])
        assert len(datasets) == 2
        assert datasets == [ds1, ds2]
        assert code == 200


def test_search_datasets_tag_multi(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets(tags=['pine', 'blue'])
        assert len(datasets) == 2
        assert datasets == [ds1, ds2]
        assert code == 200


def test_search_datasets_tag_none(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets(tags=['No'])
        assert len(datasets) == 0
        assert datasets == []
        assert code == 200


def test_search_datasets_tag_no_list(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets(tags='No')
        assert len(datasets) == 0
        assert datasets == []
        assert code == 200


def test_search_datasets_version_tag(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets(tags=['pine', 'blue'], version="0.3")
        assert len(datasets) == 1
        assert datasets == [ds2]
        assert code == 200

def test_search_datasets_multi_match_tag(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets(tags=['pine', 'blue'])
        assert len(datasets) == 2
        assert datasets == [ds1, ds2]
        assert code == 200




def test_search_datasets_version_bad_tag(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets(tags=['pIne'], version="0.3")
        assert len(datasets) == 0
        assert datasets == []
        assert code == 200


def test_search_datasets_different_version_tag(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets(tags=['pine'], version="0.3")
        assert len(datasets) == 0
        assert datasets == []
        assert code == 200

def test_search_datasets_one_ontology(test_client):
    """
    search_datasets
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        datasets, code = operations.search_datasets(ontologies=["DUO:0000018"])
        assert len(datasets) == 1
        assert datasets == [ds1]
        assert code == 200


def test_search_dataset_filters(test_client):
    """
    search_dataset_filters
    """

    _, _, context, _, _ = test_client

    with context:
        filters, code = operations.search_dataset_filters()
        assert filters == filterStruct
        assert code == 200


def test_post_change_log(test_client):
    """
    post_change_log
    """

    _, _, context, cl1, _ = test_client

    with context:
        response, code = operations.post_change_log(cl1)
        assert code == 405


def test_post_change_log_bad_key(test_client):
    """
    post_change_log
    """

    _, _, context, cl1, _ = test_client

    test_changelog_bad = {
        'nasf': "stuff",
        'version': '1.3'
    }

    with context:
        response, code = operations.post_change_log(test_changelog_bad)
        assert code == 400


def test_post_change_log_int_version(test_client):
    """
    post_change_log
    """

    _, _, context, cl1, _ = test_client

    test_changelog_bad = {
        'nasf': "stuff",
        'version': 0.5
    }

    with context:
        response, code = operations.post_change_log(test_changelog_bad)
        assert code == 400


def test_get_change_log(test_client):
    """
    get_change_log
    """

    _, _, context, cl1, _ = test_client

    with context:
        response, code = operations.get_change_log(cl1['version'])
        assert response == cl1
        assert code == 200


def test_get_versions(test_client):
    """
    get_versions
    """

    _, _, context, cl1, cl2 = test_client

    with context:
        response, code = operations.get_versions()
        assert response == [cl1['version'], cl2['version']]
        assert code == 200

def test_search_ontologies_duo(test_client):
    """
    search_dataset_ontologies
    """

    ds1, ds2, context, _, _ = test_client

    with context:
        response, code = operations.search_dataset_ontologies()
        assert code == 200
        assert response == ["DUO:0000014", "DUO:0000018"]

def load_test_objects():
    dataset_1_id = uuid.uuid4().hex
    dataset_2_id = uuid.uuid4().hex

    test_dataset_1 = {
        'id': dataset_1_id,
        'name': 'dataset_1',
        'description': 'mock profyle project for testing',
        'tags': ['candig', 'orange', 'pine'],
        'version': '0.1',
        'ontologies': [
            {"id": "duo",
             "terms": [{"id": "DUO:0000018"}, {"id": "DUO:0000014"}]}
        ]


    }

    test_dataset_2 = {
        'id': dataset_2_id,
        'name': 'dataset_2',
        'description': 'mock tf4cn project for testing',
        'tags': ['test', 'candig', 'blue'],
        'version': '0.3',
        'ontologies': [
            {"id": "duo",
             "terms": [{"id": "DUO:0000014"}]}
        ]

    }

    test_changelog_1 = {
        'log': ["stuff"],
        'version': '0.5'
    }

    test_changelog_2 = {
        'log': ["stuff"],
        'version': '1.3'
    }

    operations.post_dataset(test_dataset_1)
    operations.post_dataset(test_dataset_2)

    operations.post_change_log(test_changelog_1)
    operations.post_change_log(test_changelog_2)

    return test_dataset_1, test_dataset_2, test_changelog_1, test_changelog_2




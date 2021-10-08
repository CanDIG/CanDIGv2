"""
Methods to handle incoming service requests
"""

import json
import datetime
import uuid
import pkg_resources

import flask

from sqlalchemy import exc, or_


from candig_dataset_service.orm.models import Dataset, ChangeLog
from candig_dataset_service.orm import get_session, ORMException, dump
from candig_dataset_service.api.logging import apilog, logger
from candig_dataset_service.api.logging import structured_log as struct_log
from candig_dataset_service.api.models import Version
from candig_dataset_service.api.exceptions import IdentifierFormatError
from candig_dataset_service.ontologies.duo import OntologyParser, OntologyValidator, ont



APP = flask.current_app


def _report_search_failed(typename, exception, **kwargs):
    """
    Generate standard log message + request error for error:
    Internal error performing search
    :param typename: name of type involved
    :param exception: exception thrown by ORM
    :param **kwargs: arbitrary keyword parameters
    :return: Connexion Error() type to return
    """
    report = typename + ' search failed'
    message = 'Internal error searching for '+typename+'s'
    logger().error(struct_log(action=report, exception=str(exception), **kwargs))
    return dict(message=message, code=500)


def _report_object_exists(typename, **kwargs):
    """
    Generate standard log message + request error for warning:
    Trying to POST an object that already exists
    :param typename: name of type involved
    :param **kwargs: arbitrary keyword parameters
    :return: Connexion Error() type to return
    """
    report = typename + ' already exists'
    logger().warning(struct_log(action=report, **kwargs))
    return dict(message=report, code=405)


def _report_update_failed(typename, exception, **kwargs):
    """
    Generate standard log message + request error for error:
    Internal error performing update (PUT)
    :param typename: name of type involved
    :param exception: exception thrown by ORM
    :param **kwargs: arbitrary keyword parameters
    :return: Connexion Error() type to return
    """
    report = typename + ' updated failed'
    message = 'Internal error updating '+typename+'s'
    logger().error(struct_log(action=report, exception=str(exception), **kwargs))
    return dict(message=message, code=500)


def _report_conversion_error(typename, exception, **kwargs):
    """
    Generate standard log message + request error for warning:
    Trying to POST an object that already exists
    :param typename: name of type involved
    :param exception: exception thrown by ORM
    :param **kwargs: arbitrary keyword parameters
    :return: Connexion Error() type to return
    """
    report = 'Could not convert '+typename+' to ORM model'
    message = typename + ': failed validation - could not convert to internal representation'
    logger().error(struct_log(action=report, exception=str(exception), **kwargs))
    return dict(message=message, code=400)


def _report_write_error(typename, exception, **kwargs):
    """
    Generate standard log message + request error for error:
    Error writing to DB
    :param typename: name of type involved
    :param exception: exception thrown by ORM
    :param **kwargs: arbitrary keyword parameters
    :return: Connexion Error() type to return
    """
    report = 'Internal error writing '+typename+' to DB'
    message = typename + ': internal error saving ORM object to DB'
    logger().error(struct_log(action=report, exception=str(exception), **kwargs))
    err = dict(message=message, code=500)
    return err

@apilog
def post_dataset(body):
    """
    Creates a new dataset following the dataset_ingest
    schema defined in datasets.yaml

    The ontologies_internal property is used when looking
    up current ontologies but is not a property to be returned
    when querying the dataset.


    :param body: POST request body
    :type body: object

    :returns: body, 201 on success, error code on failure
    :rtype: object, int 

    .. note::
        Refer to the OpenAPI Spec for a proper schemas of dataset_ingest and dataset objects.

    """

    db_session = get_session()

    if not body.get('id'):
        iid = uuid.uuid1()
        body['id'] = iid
    else:
        iid = body['id']

    if not body.get('version'):
        body['version'] = Version

    body['created'] = datetime.datetime.utcnow()
    mapped = []

    if body.get('ontologies'):

        # Ontology objects should be {'id': ontology_name, 'terms': [{'id': 'some code'}]}

        mapped = {ontology['id']: ontology['terms'] for ontology in body['ontologies']}
        if 'duo' in mapped.keys():
            validator = OntologyValidator(ont=ont, input_json=mapped)
            valid, invalids = validator.validate_duo()

            if not valid:
                err = dict(message="DUO Validation Errors encountered: " + str(invalids), code=400)
                return err, 400

            duo_terms = json.loads(validator.get_duo_list())
            duos = []

            for term in duo_terms:
                stuff = OntologyParser(ont, term["id"]).get_overview()
                duos.append({**term, **stuff})

            body['ontologies'] = duos
    body['ontologies_internal'] = mapped

    try:
        orm_dataset = Dataset(**body)
    except TypeError as e:
        err = _report_conversion_error('dataset', e, **body)
        return err, 400

    try:
        db_session.add(orm_dataset)
        db_session.commit()
    except exc.IntegrityError:
        db_session.rollback()
        err = _report_object_exists('dataset: ' + body['id'], **body)
        return err, 405
    except ORMException as e:
        db_session.rollback()
        err = _report_write_error('dataset', e, **body)
        return err, 500

    body.pop('ontologies_internal')
    return body, 201


@apilog
def get_dataset_by_id(dataset_id):
    """
    :param dataset_id: UUID
    :type dataset_id: string

    :return: dataset specified by UUID, 200 on success. Error code on failure.
    :rtype: dataset schema, int
    """
    db_session = get_session()

    try:
        validate_uuid_string('id', dataset_id)
        specified_dataset = db_session.query(Dataset) \
            .get(dataset_id)
    except IdentifierFormatError as e:
        err = dict(
            message=str(e),
            code=404)
        return err, 404

    if not specified_dataset:
        err = dict(message="Dataset not found: " + str(dataset_id), code=404)
        return err, 404

    return dump(specified_dataset), 200


@apilog
def delete_dataset_by_id(dataset_id):
    """
    Current thoughts are that delete should only be a CLI accessible command
    rather than API

    :param dataset_id: UUID
    :return: 204 on successful delete
    """
    db_session = get_session()

    try:
        specified_dataset = db_session.query(Dataset) \
            .get(dataset_id)
    except ORMException as e:
        err = _report_search_failed('call', e, dataset_id=str(dataset_id))
        return err, 500

    if not specified_dataset:
        err = dict(message="Dataset not found: " + str(dataset_id), code=404)
        return err, 404

    try:
        row = db_session.query(Dataset).filter(Dataset.id == dataset_id).first()
        db_session.delete(row)
        db_session.commit()
    except ORMException as e:
        err = _report_update_failed('dataset', e, dataset_id=str(dataset_id))
        return err, 500

    return None, 204


@apilog
def search_datasets(tags=None, version=None, ontologies=None):
    """
    :param tags: List of strings
    :param version: List of strings
    :param ontologies: List of ontology terms
    :return: List of datasets matching any of the supplied parameters
    """
    db_session = get_session()
    print(tags, version, ontologies)
    try:
        datasets = db_session.query(Dataset)
        if version:
            datasets = datasets.filter(Dataset.version.like('%' + version + '%'))
        if tags:
            # return any project that matches at least one tag
            datasets = datasets.filter(or_(*[Dataset.tags.contains(tag) for tag in tags]))
        if ontologies:
            datasets = datasets.filter(or_(*[Dataset.ontologies_internal.contains(term) for term in ontologies]))

    except ORMException as e:
        err = _report_search_failed('dataset', e)
        return err, 500
    return [dump(x) for x in datasets], 200


@apilog
def search_dataset_filters():
    """
    Searches through filters specified in orm/filters_search.json

    :return: List of filters for project searches
    :rtype: object
    """
    valid_filters = ["tags", "version"]

    return get_search_filters(valid_filters)


@apilog
def get_search_filters(valid_filters):
    """
    Helper for search_dataset_filters

    :param valid_filters: List of filter names currently valid in the system
    :return: List of filter structures matching the names in valid_filters
    """
    filter_file = pkg_resources.resource_filename('candig_dataset_service',
                                                  'orm/filters_search.json')

    with open(filter_file, 'r') as filters:
        search_filters = json.load(filters)

    response = []

    for search_filter in search_filters:
        if search_filter["filter"] in valid_filters:
            response.append(search_filter)

    return response, 200


@apilog
def search_dataset_ontologies():
    """
    Queries the dataset database for all ontology terms used by the stored datasets.

    :return: List of all ontologies currently used by datasets
    """

    db_session = get_session()
    try:
        datasets = db_session.query(Dataset)

        valid = datasets.filter(Dataset.ontologies != [])

        ontologies = [dump(x)['ontologies'] for x in valid]

        terms = sorted(list(set([term['id'] for ontology in ontologies for term in ontology])))

    except ORMException as e:
        err = _report_search_failed('dataset', e)
        return err, 500

    return terms, 200

def search_dataset_discover(tags=None, version=None):
    """
    Discovery methods are not implemented at this time
    """
    err = dict(
        message="Not implemented",
        code=501
    )

    return err, 501


def get_datasets_discover_filters(tags=None, version=None):
    """
    Discovery methods are not implemented at this time
    """
    err = dict(
        message="Not implemented",
        code=501
    )
    return err, 501


@apilog
def post_change_log(body):
    """
    Create a new change log following the changeLog
    schema in datasets.yaml

    :param body: POST body object following the changeLog schema
    :type body: object

    :return: body, 200 on success
    """
    db_session = get_session()
    change_version = body.get('version')

    body['created'] = datetime.datetime.utcnow()

    try:
        orm_changelog = ChangeLog(**body)
    except TypeError as e:
        err = _report_conversion_error('changelog', e, **body)
        return err, 400

    try:
        db_session.add(orm_changelog)
        db_session.commit()
    except exc.IntegrityError:
        db_session.rollback()
        err = _report_object_exists('changelog: ' + body['version'], **body)
        return err, 405
    except ORMException as e:
        err = _report_write_error('changelog', e, **body)
        return err, 500

    logger().info(struct_log(action='post_change_log', status='created',
                             change_version=change_version, **body))

    return body, 201



@apilog
def get_versions():
    """
    Query the change logs for and gather all the versions
    to return. 

    :return: List of release versions of the database
    :rtype: string
    """
    db_session = get_session()
    change_log = ChangeLog

    try:
        versions = db_session.query(change_log.version)
    except ORMException as e:
        err = _report_search_failed('versions', e)
        return err, 500

    return [entry.version for entry in versions], 200


@apilog
def get_change_log(version):
    """
    Query the database for a specific change log based on version

    :param version: required release version
    :return: changes associated with specified release version
    """
    db_session = get_session()
    change_log = ChangeLog

    try:
        log = db_session.query(change_log)\
            .get(version)
    except ORMException as e:
        err = _report_search_failed('change log', e)
        return err, 500

    if not log:
        err = dict(message="Change log not found", code=404)
        return err, 404

    return dump(log), 200


def validate_uuid_string(field_name, uuid_str):
    """
    Validate that the id parameter is a valid UUID string

    :param uuid_str: query parameter
    :param field_name: id field name
    """
    try:
        uuid.UUID(uuid_str)
    except ValueError:
        raise IdentifierFormatError(field_name)
    return


# pylint: disable=invalid-name
# pylint: disable=C0301
"""
Implement endpoints of model service
"""
import datetime
import uuid
import flask
import os
import json
import pkg_resources
import loompy
import hashlib

from sqlalchemy import or_
from sqlalchemy import exc
from candig_rnaget import orm
from candig_rnaget.api.logging import apilog, logger
from candig_rnaget.api.logging import structured_log as struct_log
from candig_rnaget.api.models import BasePath, Version
from candig_rnaget.api.exceptions import IdentifierFormatError
from candig_rnaget.expression.rnaget_query import ExpressionQueryTool, UnsupportedOutputError
from candig_rnaget.expression.rnaget_query import SUPPORTED_OUTPUT_FORMATS

app = flask.current_app


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
    report = typename + 'already exists'
    logger().warning(struct_log(action=report, **kwargs))
    return dict(message=report, code=405)


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


def md5(file_path):
    """
    Generate md5checksum for an input file

    :param file_path: absolute path to the input file
    :return: hex digest of the md5 hash
    """
    m_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        f_bytes = f.read()
        m_hash.update(f_bytes)
    return m_hash.hexdigest()


@apilog
def get_project_by_id(projectId):
    """

    :param projectId:
    :return: all projects or if projectId specified, corresponding project
    """
    db_session = orm.get_session()
    project = orm.models.Project

    try:
        validate_uuid_string('id', projectId)
        specified_project = db_session.query(project)\
            .get(projectId)
    except IdentifierFormatError as e:
        err = dict(
            message=str(e),
            code=404)
        return err, 404

    if not specified_project:
        err = dict(message="Project not found: "+str(projectId), code=404)
        return err, 404

    return orm.dump(specified_project), 200


@apilog
def post_project(body):
    db_session = orm.get_session()

    if not body.get('id'):
        iid = uuid.uuid1()
        body['id'] = iid
    else:
        iid = body['id']

    if not body.get('version'):
        body['version'] = Version

    body['created'] = datetime.datetime.utcnow()

    try:
        orm_project = orm.models.Project(**body)
    except TypeError as e:
        err = _report_conversion_error('project', e, **body)
        return err, 400

    try:
        db_session.add(orm_project)
        db_session.commit()
    except exc.IntegrityError:
        db_session.rollback()
        err = _report_object_exists('project: ' + body['id'], **body)
        return err, 405
    except orm.ORMException as e:
        db_session.rollback()
        err = _report_write_error('project', e, **body)
        return err, 500

    logger().info(struct_log(action='post_project', status='created',
                             project_id=str(iid), **body))

    return body, 201, {'Location': BasePath + '/projects/' + str(iid)}


@apilog
def search_projects(tags=None, version=None):
    """

    :param tags:
    :param version:
    :return:
    """
    db_session = orm.get_session()
    project = orm.models.Project

    try:
        projects = db_session.query(project)
        if version:
            projects = projects.filter(project.version.like('%' + version + '%'))
        if tags:
            # return any project that matches at least one tag
            projects = projects.filter(or_(*[project.tags.contains(tag) for tag in tags]))
    except orm.ORMException as e:
        err = _report_search_failed('project', e)
        return err, 500

    return [orm.dump(x) for x in projects], 200


@apilog
def search_project_filters():
    """
    :return: filters for project searches
    """
    valid_filters = ["version"]

    return get_search_filters(valid_filters)


@apilog
def get_study_by_id(studyId):
    """

    :param studyId: required identifier
    :return: a single specified study
    """
    db_session = orm.get_session()
    study = orm.models.Study

    try:
        validate_uuid_string('studyID', studyId)
        specified_study = db_session.query(study)\
            .get(studyId)

    except IdentifierFormatError as e:
        err = dict(
            message=str(e),
            code=404)
        return err, 404

    if not specified_study:
        err = dict(message="Study not found: " + studyId, code=404)
        return err, 404

    return orm.dump(specified_study), 200


@apilog
def post_study(body):
    db_session = orm.get_session()

    if not body.get('id'):
        iid = uuid.uuid1()
        body['id'] = iid
    else:
        iid = body['id']

    if not body.get('version'):
        body['version'] = Version

    body['created'] = datetime.datetime.utcnow()

    try:
        orm_study = orm.models.Study(**body)
    except TypeError as e:
        err = _report_conversion_error('study', e, **body)
        return err, 400

    try:
        db_session.add(orm_study)
        db_session.commit()
    except exc.IntegrityError:
        db_session.rollback()
        err = _report_object_exists('study: ' + body['id'], **body)
        return err, 405
    except orm.ORMException as e:
        db_session.rollback()
        err = _report_write_error('study', e, **body)
        return err, 500

    logger().info(struct_log(action='post_study', status='created',
                             project_id=str(iid), **body))

    return body, 201, {'Location': BasePath + '/studies/' + str(iid)}


@apilog
def search_studies(tags=None, version=None):
    """

    :param tags: optional list of tags
    :param version:
    :param projectID:
    :return: studies that match the filters
    """
    db_session = orm.get_session()
    study = orm.models.Study

    try:
        studies = db_session.query(study)
        if version:
            studies = studies.filter(study.version.like('%' + version + '%'))
        if tags:
            # return any study that matches at least one tag
            studies = studies.filter(or_(*[study.tags.contains(tag) for tag in tags]))

    except IdentifierFormatError as e:
        _report_search_failed('project', e)
        return [], 200

    except orm.ORMException as e:
        err = _report_search_failed('project', e)
        return err, 500

    return [orm.dump(x) for x in studies], 200


@apilog
def search_study_filters():
    """
    :return: filters for study searches
    """
    valid_filters = ["version"]

    return get_search_filters(valid_filters)


def get_search_filters(valid_filters):
    filter_file = pkg_resources.resource_filename('candig_rnaget', 'orm/filters_search.json')

    with open(filter_file, 'r') as ef:
        search_filters = json.load(ef)

    response = []

    for search_filter in search_filters:
        if search_filter["filter"] in valid_filters:
            response.append(search_filter)

    return response, 200


def get_expression_bytes_by_id(expressionId, sampleIDList=None, featureIDList=None, featureNameList=None):
    """
    :param expressionId: required identifier
    :return: a single specified expression matrix
    """
    db_session = orm.get_session()
    expression = orm.models.File

    try:
        validate_uuid_string('id', expressionId)
        expr_matrix = db_session.query(expression).get(expressionId)

        if not expr_matrix:
            err = dict(message="Expression matrix not found: " + expressionId, code=404)
            return err, 404

        if not any([sampleIDList, featureIDList, featureNameList]):
            response = flask.send_file(expr_matrix.__filepath__, as_attachment=True)
            response.direct_passthrough = False
            return response, 200

        else:

            if expr_matrix.fileType == "loom":
                h5_filepath = expr_matrix.__filepath__.split(".loom")[0] + ".h5"
                h5_expr_matrix = db_session.query(expression).filter(expression.__filepath__ == h5_filepath).one()

            file_response = slice_expression_data(
                h5_expr_matrix, sampleIDList, featureIDList, featureNameList, None, None, 'loom'
            )

            if file_response:
                response = flask.send_file(file_response['__filepath__'], as_attachment=True)
                response.direct_passthrough = False
                return response, 200

    except IdentifierFormatError as e:
        err = dict(
            message=str(e),
            code=404)
        return err, 404


@apilog
def get_expression_tickets_by_id(expressionId, sampleIDList=None, featureIDList=None, featureNameList=None):
    """

    :param expressionId: required identifier
    :return: a single specified expression matrix
    """
    db_session = orm.get_session()
    expression = orm.models.File

    try:
        validate_uuid_string('id', expressionId)

        expr_matrix = db_session.query(expression).get(expressionId)

        if not expr_matrix:
            err = dict(message="Expression matrix not found: " + expressionId, code=404)
            return err, 404

        if not any([sampleIDList, featureIDList, featureNameList]):
            return orm.dump(expr_matrix), 200

        else:

            if expr_matrix.fileType == "loom":
                h5_filepath = expr_matrix.__filepath__.split(".loom")[0] + ".h5"
                h5_expr_matrix = db_session.query(expression).filter(expression.__filepath__ == h5_filepath).one()

            file_response = slice_expression_data(
                h5_expr_matrix, sampleIDList, featureIDList, featureNameList, None, None, 'loom'
            )

            if file_response:
                return file_response, 200

    except IdentifierFormatError as e:
        err = dict(
            message=str(e),
            code=404)
        return err, 404


@apilog
def post_expression(body):
    db_session = orm.get_session()

    if body.get('__filepath__'):
        file_path = body['__filepath__']
        if not os.path.isfile(file_path):
            err = dict(message="Invalid file path: " + file_path, code=400)
            return err, 400
        body['md5'] = md5(file_path)
    else:
        err = dict(message="An absolute __filepath__ is required", code=400)
        return err, 400

    if not body.get('id'):
        iid = uuid.uuid1()
        body['id'] = iid
    else:
        iid = body['id']

    if not body.get('version'):
        body['version'] = Version

    if not body.get('url'):
        base_url = app.config.get('BASE_DL_URL') + BasePath
        body['url'] = base_url + '/expressions/download/' + os.path.basename(file_path)

    body['created'] = datetime.datetime.utcnow()

    try:
        orm_expression = orm.models.File(**body)
    except TypeError as e:
        err = _report_conversion_error('file', e, **body)
        return err, 400

    try:
        db_session.add(orm_expression)
        db_session.commit()
    except exc.IntegrityError:
        db_session.rollback()
        err = _report_object_exists('expression: ' + body['url'], **body)
        return err, 405
    except orm.ORMException as e:
        db_session.rollback()
        err = _report_write_error('expression', e, **body)
        return err, 500

    logger().info(struct_log(action='post_expression', status='created',
                             expression_id=str(iid), **body))

    return body, 201, {'Location': BasePath + '/expressions/' + str(iid)}


@apilog
def get_expression_formats():
    """
    :return: array of supported expression formats
    """
    formats = SUPPORTED_OUTPUT_FORMATS
    if not formats:
        return [], 404
    return formats, 200


def get_search_expressions_bytes(tags=None, sampleIDList=None, projectID=None, studyID=None,
                                 version=None, featureIDList=None, featureNameList=None,
                                 minExpression=None, maxExpression=None, format="h5"):
    """

    :param tags: optional Comma separated tag list
    :param sampleIDList: optional list of sample identifiers
    :param projectID: optional project identifier
    :param studyID: optional study identifier
    :param version: optional version
    :param featureIDList: optional filter by listed feature IDs
    :param featureNameList: optional filter by listed features
    :param format: output file type (not a part of schema yet)
    :return: expression matrices matching filters
    """

    try:
        expressions = filter_expression_data(version, tags, studyID, projectID)

        if not any([sampleIDList, featureIDList, featureNameList, maxExpression, minExpression]):
            expressions = filter_expression_format(expressions, format)
        else:
            expressions = filter_expression_format(expressions, format='h5')
            if minExpression:
                minExpression = json.loads(','.join(minExpression))
            if maxExpression:
                maxExpression = json.loads(','.join(maxExpression))
            responses = []

            try:
                for expr in expressions:
                    file_response = slice_expression_data(
                        expr, sampleIDList, featureIDList, featureNameList, minExpression, maxExpression, format
                    )

                    if file_response:
                        response = flask.send_file(file_response['__filepath__'], as_attachment=True)
                        response.direct_passthrough = False
                        return response, 200

            except (ValueError, UnsupportedOutputError) as e:
                err = dict(
                    message=str(e),
                    code=400)
                return err, 400

            if len(responses) > 0:
                return responses[0], 200

    except IdentifierFormatError as e:
        _report_search_failed('expression', e)
        return [], 200

    except orm.ORMException as e:
        err = _report_search_failed('expression', e)
        return err, 500

    filepath = get_expression_file_path_by_id([orm.dump(expr_matrix) for expr_matrix in expressions][0]['id'])

    response = flask.send_file(filepath, as_attachment=True)
    response.direct_passthrough = False
    return response, 200


@apilog
def get_search_expressions(tags=None, sampleIDList=None, projectID=None, studyID=None,
                           version=None, featureIDList=None, featureNameList=None,
                           minExpression=None, maxExpression=None, format="h5"):
    """

    :param tags: optional Comma separated tag list
    :param sampleIDList: optional list of sample identifiers
    :param projectID: optional project identifier
    :param studyID: optional study identifier
    :param version: optional version
    :param featureIDList: optional filter by listed feature IDs
    :param featureNameList: optional filter by listed features
    :param format: output file type (not a part of schema yet)
    :return: expression matrices matching filters
    """

    try:
        expressions = filter_expression_data(version, tags, studyID, projectID)

        if not any([sampleIDList, featureIDList, featureNameList, maxExpression, minExpression]):
            expressions = filter_expression_format(expressions, format)
        else:
            expressions = filter_expression_format(expressions, format='h5')
            if minExpression:
                minExpression = json.loads(','.join(minExpression))
            if maxExpression:
                maxExpression = json.loads(','.join(maxExpression))
            responses = []
            try:
                for expr in expressions:
                    file_response = slice_expression_data(
                        expr, sampleIDList, featureIDList, featureNameList, minExpression, maxExpression, format
                    )
                    if file_response:
                        return file_response, 200
                    else:
                        return [], 200

            except (ValueError, UnsupportedOutputError) as e:
                err = dict(
                    message=str(e),
                    code=400)
                return err, 400

            if len(responses) > 0:
                return responses[0], 200

    except IdentifierFormatError as e:
        _report_search_failed('expression', e)
        return [], 200

    except orm.ORMException as e:
        err = _report_search_failed('expression', e)
        return err, 500

    return [orm.dump(expr_matrix) for expr_matrix in expressions][0], 200


@apilog
def post_search_expressions(body):

    # Parse search object
    version = body.get("version")
    tags = body.get("tags")
    studyID = body.get("studyID")
    projectID = body.get("projectID")
    sampleIDList = body.get("sampleIDList")
    featureIDList = body.get("featureIDList")
    featureNameList = body.get("featureNameList")
    maxExpression = body.get("maxExpression")
    minExpression = body.get("minExpression")

    # If not supplied, set defaults
    file_type = body.get("format", "h5")

    try:
        expressions = filter_expression_data(version, tags, studyID, projectID)

        if not any([sampleIDList, featureIDList, featureNameList, maxExpression, minExpression]):
            expressions = filter_expression_format(expressions, format)
        else:
            # H5 queries
            responses = []
            try:
                for expr in expressions:
                    file_response = slice_expression_data(
                        expr, sampleIDList, featureIDList, featureNameList, minExpression, maxExpression, file_type
                    )
                    if file_response:
                        responses.append(file_response)

            except (ValueError, UnsupportedOutputError) as e:
                err = dict(
                    message=str(e),
                    code=400)
                return err, 400

            return responses, 200

    except IdentifierFormatError as e:
        _report_search_failed('expression', e)
        return [], 200

    except orm.ORMException as e:
        err = _report_search_failed('expression', e)
        return err, 500

    return [orm.dump(expr_matrix) for expr_matrix in expressions], 200


def filter_expression_data(version, tags, study_id, project_id):
    """
    Performs the database queries to filter expression files
    """
    db_session = orm.get_session()
    expression = orm.models.File

    # TODO: find better way to filter for expression data?
    expressions = db_session.query(expression)

    # db queries
    if version:
        expressions = expressions.filter(expression.version.like('%' + version + '%'))
    if tags:
        # return any project that matches at least one tag
        expressions = expressions.filter(or_(*[expression.tags.contains(tag) for tag in tags]))
    if study_id:
        validate_uuid_string('studyID', study_id)
        expressions = expressions.filter(expression.studyID == study_id)
    if project_id:
        validate_uuid_string('projectID', project_id)
        study_list = get_study_by_project(project_id)
        expressions = expressions.filter(expression.studyID.in_(study_list))

    return expressions


def filter_expression_format(expressions, format):
    """
    Note: No file format conversion at this point
    :param expression: list of orm expression objects
    :param format: desired file format
    :return: filtered orm of expression objects
    """
    expression = orm.models.File
    return expressions.filter(expression.fileType == format)


def slice_expression_data(expr, sampleIDList, featureIDList, featureNameList, minExpression, maxExpression, file_type):
    """
    Performs the slicing on each expression file
    :param threshold_input_type:
    :return: temporary file response object
    """
    tmp_dir = app.config.get('TMP_DIRECTORY')

    output_file_id = uuid.uuid1()
    output_filepath = tmp_dir + str(output_file_id) + '.' + file_type
    feature_map = pkg_resources.resource_filename('candig_rnaget',
                                                  'expression/feature_mapping_HGNC.tsv')

    try:
        h5query = ExpressionQueryTool(
            expr.__filepath__,
            output_filepath,
            include_metadata=False,
            output_type=file_type,
            feature_map=feature_map
        )

        if minExpression or maxExpression:
            q = h5query.search_threshold(min_ft=minExpression, max_ft=maxExpression, feature_id_list=featureIDList,
                                         feature_name_list=featureNameList, samples=sampleIDList)
        else:
            q = h5query.search(samples=sampleIDList, feature_id_list=featureIDList, feature_name_list=featureNameList)

        h5query.close()

    # HDF5 file error
    except OSError as err:
        logger().warning(struct_log(action=str(err)))
        return None

    # Given feature list or sample ID does not contain any valid entries
    except LookupError as err:
        logger().warning(struct_log(action=str(err)))
        return None

    return generate_file_response(q, file_type, output_file_id, expr.studyID, expr.units)


@apilog
def get_expressions():
    """

    :return: available expression matrices
    """
    return get_search_expressions()


@apilog
def search_expression_filters(type=None):
    """

    :param type: type of filter to return
    :return: filters for expression searches
    """
    filter_file = pkg_resources.resource_filename('candig_rnaget', 'orm/filters_expression.json')

    with open(filter_file, 'r') as ef:
        expression_filters = json.load(ef)

    if type:
        response = expression_filters.get(type, [])
    else:
        response = []
        for filter_key in expression_filters:
            response += expression_filters[filter_key]

    return response, 200


@apilog
def get_versions():
    """

    :return: release versions of the database
    """
    db_session = orm.get_session()
    change_log = orm.models.ChangeLog

    try:
        versions = db_session.query(change_log.version)
    except orm.ORMException as e:
        err = _report_search_failed('versions', e)
        return err, 500

    return [entry.version for entry in versions], 200


@apilog
def post_change_log(body):
    db_session = orm.get_session()
    change_version = body.get('version')

    body['created'] = datetime.datetime.utcnow()

    try:
        orm_changelog = orm.models.ChangeLog(**body)
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
    except orm.ORMException as e:
        err = _report_write_error('changelog', e, **body)
        return err, 500

    logger().info(struct_log(action='post_change_log', status='created',
                             change_version=change_version, **body))

    return body, 201, {'Location': BasePath + '/changelog/' + change_version}


@apilog
def get_change_log(version):
    """

    :param version: required release version
    :return: changes associated with specified release version
    """
    db_session = orm.get_session()
    change_log = orm.models.ChangeLog

    try:
        log = db_session.query(change_log)\
            .get(version)
    except orm.ORMException as e:
        err = _report_search_failed('change log', e)
        return err, 500

    if not log:
        err = dict(message="Change log not found", code=404)
        return err, 404

    return orm.dump(log), 200


@apilog
def get_file(fileID):
    """

    :param fileID: required identifier
    :return: a single specified file download URL
    """
    db_session = orm.get_session()
    file = orm.models.File

    try:
        validate_uuid_string('fileID', fileID)
        file_q = db_session.query(file).get(fileID)
    except IdentifierFormatError as e:
        err = dict(
            message=str(e),
            code=404)
        return err, 404
    except orm.ORMException as e:
        err = _report_search_failed('file', e, file_id=fileID)
        return err, 500

    if not file_q:
        err = dict(message="File not found: " + fileID, code=404)
        return err, 404

    return orm.dump(file_q), 200


@apilog
def search_files(tags=None, projectID=None, studyID=None, fileType=None):
    """

    :param tags: optional comma separated tag list
    :param projectID: optional project identifier
    :param studyID: optional study identifier
    :param fileType: optional file type
    :return: manifest of download URL(s) for matching files
    """
    db_session = orm.get_session()
    file = orm.models.File

    try:
        files = db_session.query(file)
        if tags:
            files = files.filter(or_(*[file.tags.contains(tag) for tag in tags]))
        if projectID:
            validate_uuid_string('projectID', projectID)
            study_list = get_study_by_project(projectID)
            files = files.filter(file.studyID.in_(study_list))
        if studyID:
            validate_uuid_string('studyID', studyID)
            files = files.filter(file.studyID == studyID)
        if fileType:
            files = files.filter(file.fileType == fileType)
    except IdentifierFormatError as e:
        _report_search_failed('file', e)
        return [], 200
    except orm.ORMException as e:
        err = _report_search_failed('file', e)
        return err, 500

    return [orm.dump(x) for x in files], 200


def get_study_by_project(projectID):
    """

    :param projectID:
    :return: list of study id's associated with a given project
    """
    db_session = orm.get_session()
    study = orm.models.Study
    study_id_list = []
    studies = db_session.query(study.id)\
        .filter(study.parentProjectID == projectID)
    if studies:
        study_id_list = [x.id for x in studies]
    return study_id_list


def get_continuous_by_id(continuousId):
    """
    TODO: Implement
    """

    err = dict(
        message="Not implemented",
        code=501
    )
    return err, 501


@apilog
def get_continuous_formats():
    """
    :return: array of supported data formats
    """
    formats = ["tsv"]
    return formats, 200


def search_continuous(format=None):
    """
    TODO: Implement
    """

    err = dict(
        message="Not implemented",
        code=501
    )
    return err, 501


def search_continuous_filters():
    """
    :return: filters for continuous searches
    """
    filter_file = pkg_resources.resource_filename("candig_rnaget", "orm/filters_continuous.json")

    with open(filter_file, "r") as ef:
        continuos_filters = json.load(ef)

    response = [continuos_filters]

    return response, 200


def get_search_continuousId_ticket(continuousId=None):
    """
    TODO: Implement
    """

    err = dict(
        message="Not implemented",
        code=501
    )
    return err, 501


def get_search_continuousId_bytes(continuousId=None):
    """
    TODO: Implement
    """

    err = dict(
        message="Not implemented",
        code=501
    )
    return err, 501


def get_search_continuous_bytes():
    """
    TODO: Implement
    """

    err = dict(
        message="Not implemented",
        code=501
    )
    return err, 501


def generate_file_response(results, file_type, file_id, study_id, units):
    base_url = app.config.get('BASE_DL_URL') + BasePath
    tmp_dir = app.config.get('TMP_DIRECTORY')

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    if file_type == "json":
        tmp_file_path = os.path.join(tmp_dir, str(file_id)+'.json')
        with open(tmp_file_path, 'w') as outfile:
            json.dump(results, outfile)

    elif file_type == "h5":
        tmp_file_path = results.filename
        results.close()  # writes temp file to disk

    elif file_type == "loom":
        tmp_file_path = results["filename"]
        loompy.create(tmp_file_path, results["matrix"], results["ra"], results["ca"])

    else:
        raise ValueError("Invalid file type")

    m_hash = md5(tmp_file_path)

    file_record = {
        'id': file_id,
        'url': base_url + '/download/' + str(file_id),
        'studyID': study_id,
        'fileType': file_type,
        'version': Version,
        'units': units,
        'created': datetime.datetime.utcnow(),
        'md5': m_hash,
        '__filepath__': tmp_file_path
    }

    return create_tmp_file_record(file_record)


def get_expression_file_path_by_id(file_id):
    """

    :param expressionId: required identifier
    :return: internal expression matrix filepath
    """
    db_session = orm.get_session()
    file = orm.models.File

    try:
        file = db_session.query(file).filter(file.id == file_id).one()

    except orm.ORMException as e:
        err = _report_search_failed('file', e, id=file_id)
        return err, 404

    return file.__filepath__


def get_expression_file_path(file):
    """

    :param expressionId: required identifier
    :return: internal expression matrix filepath
    """
    db_session = orm.get_session()
    expression = orm.models.File
    base_url = app.config.get('BASE_DL_URL') + BasePath
    file_url = base_url + '/expressions/download/' + file

    try:
        expr_matrix = db_session.query(expression).filter(expression.url == file_url).one()

    except orm.ORMException as e:
        err = _report_search_failed('file', e, url=file_url)
        return err, 404

    return expr_matrix.__filepath__


def create_tmp_file_record(file_record):
    db_session = orm.get_session()

    try:
        orm_expression = orm.models.TempFile(**file_record)
    except TypeError as e:
        err = _report_conversion_error('file', e, **file_record)
        return err, 400

    # del file_record['__filepath__']

    try:
        db_session.add(orm_expression)
        db_session.commit()
    except exc.IntegrityError:
        err = _report_object_exists('file: ' + file_record['id'], **file_record)
        return err, 405
    except orm.ORMException as e:
        err = _report_write_error('file', e, **file_record)
        return err, 500

    return file_record


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

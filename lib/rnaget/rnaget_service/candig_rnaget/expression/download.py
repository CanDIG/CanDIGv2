"""
Download endpoints for expression data
"""

import flask
import json
import os

from sqlalchemy import exc
from candig_rnaget import orm
from candig_rnaget.api.operations import get_expression_file_path


def tmp_download(token):
    """

    :param token: for now using the file identifier
    :return: a generated tmp file with previously specified file format
    """
    return download_file(token, temp_file=True)


def persistent_download(file):
    """

    :param file: expression file name
    :return: file attachment type application/octet-stream
    """
    return download_file(file)


def download_file(token, temp_file=False):
    """

    :param token: file identifier
    :param temp_file: boolean specifier for temporary files
    :return: Content-Type string
    """

    try:
        if not temp_file:
            access_file = get_expression_file_path(token)
            if isinstance(access_file, tuple):
                return download_error("File not found", 404)
            mimetype = get_mimetype(token.split(".")[-1])
            response = flask.send_file(access_file, as_attachment=True, mimetype=mimetype)
        # use tmp directory file ID's
        else:
            db_session = orm.get_session()
            temp_file = orm.models.TempFile

            try:
                access_file = db_session.query(temp_file).get(token)
            except exc.StatementError:
                return download_error("Invalid file token: " + str(token), 400)
            if not access_file:
                return download_error("File not found (link may have expired)", 404)

            file_path = access_file.__filepath__

            if os.path.isfile(file_path):
                mimetype = get_mimetype(access_file.fileType)
                if access_file.fileType == "json":
                    with open(file_path, 'r') as json_file:
                        data = json.load(json_file)
                    response = flask.make_response(json.dumps(data))
                else:
                    response = flask.send_file(file_path, as_attachment=True, mimetype=mimetype)
            else:
                return download_error("File not found (link may have expired)", 404)

        response.direct_passthrough = False
        return response

    except (orm.ORMException, FileNotFoundError):
        message = "Something went wrong while generating your file. Please try again or contact alipski@bcgsc.ca"
        return download_error(message, 500)


def get_mimetype(file_type):
    """

    :param file_type: file format
    :return: Content-Type string
    """
    if file_type == "json":
        return "application/vnd.ga4gh.rnaget.v1.0.0+json"
    elif file_type == "loom":
        return "application/vnd.loom"
    elif file_type == "h5":
        return "application/vnd.h5"


def download_error(message, code):
    """

    :param message: error message
    :param code: error code
    :return: Response object
    """
    error_body = dict(
        message=message,
        code=code
    )
    resp = flask.make_response(json.dumps(error_body), code)
    resp.headers['Content-Type'] = "application/problem+json"
    return resp

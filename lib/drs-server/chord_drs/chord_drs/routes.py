import re

from bento_lib.responses import flask_errors
from flask import (
    Blueprint,
    current_app,
    jsonify,
    url_for,
    request,
    send_file,
    make_response
)
from sqlalchemy.orm.exc import NoResultFound
from typing import Optional
from urllib.parse import urljoin, urlparse

from chord_drs import __version__
from chord_drs.constants import SERVICE_NAME, SERVICE_TYPE
from chord_drs.data_sources import DATA_SOURCE_LOCAL, DATA_SOURCE_MINIO
from chord_drs.db import db
from chord_drs.models import DrsObject, DrsBundle
from chord_drs.utils import drs_file_checksum


RE_STARTING_SLASH = re.compile(r"^/")

drs_service = Blueprint("drs_service", __name__)


def get_drs_base_path():
    base_path = request.host

    if current_app.config["CHORD_URL"]:
        parsed_chord_url = urlparse(current_app.config["CHORD_URL"])
        base_path = f"{parsed_chord_url.netloc}{parsed_chord_url.path}"

        if current_app.config["CHORD_SERVICE_URL_BASE_PATH"]:
            base_path = urljoin(
                base_path, re.sub(
                    RE_STARTING_SLASH, "", current_app.config["CHORD_SERVICE_URL_BASE_PATH"]
                )
            )

    return base_path


def create_drs_uri(object_id: str) -> str:
    return f"drs://{get_drs_base_path()}/{object_id}"


def build_bundle_json(drs_bundle: DrsBundle, inside_container: bool = False) -> dict:
    content = []
    bundles = DrsBundle.query.filter_by(parent_bundle=drs_bundle).all()

    for bundle in bundles:
        obj_json = build_bundle_json(bundle, inside_container=inside_container)
        content.append(obj_json)

    for child in drs_bundle.objects:
        obj_json = build_object_json(child, inside_container=inside_container)
        content.append(obj_json)

    response = {
        "contents": content,
        "checksums": [
            {
                "checksum": drs_bundle.checksum,
                "type": "sha-256"
            },
        ],
        "created_time": f"{drs_bundle.created.isoformat('T')}Z",
        "size": drs_bundle.size,
        "name": drs_bundle.name,
        "description": drs_bundle.description,
        "id": drs_bundle.id,
        "self_uri": create_drs_uri(drs_bundle.id)
    }

    return response


def build_object_json(drs_object: DrsObject, inside_container: bool = False) -> dict:
    # TODO: This access type is wrong in the case of http (non-secure)
    # TODO: I'll change it to http for now, will think of a way to fix this
    data_source = current_app.config["SERVICE_DATA_SOURCE"]
    default_access_method = {
        "access_url": {
            "url": url_for("drs_service.object_download", object_id=drs_object.id, _external=True)
        },
        "type": "http"
    }

    if inside_container and data_source == DATA_SOURCE_LOCAL:
        access_methods = [
            default_access_method,
            {
                "access_url": {
                    "url": f"file://{drs_object.location}"
                },
                "type": "file"
            }
        ]
    elif data_source == DATA_SOURCE_MINIO:
        access_methods = [
            default_access_method,
            {
                "access_url": {
                    "url": drs_object.location
                },
                "type": "s3"
            }
        ]
    else:
        access_methods = [default_access_method]

    response = {
        "access_methods": access_methods,
        "checksums": [
            {
                "checksum": drs_object.checksum,
                "type": "sha-256"
            },
        ],
        "created_time": f"{drs_object.created.isoformat('T')}Z",
        "size": drs_object.size,
        "name": drs_object.name,
        "description": drs_object.description,
        "id": drs_object.id,
        "self_uri": create_drs_uri(drs_object.id)
    }

    return response


@drs_service.route("/service-info", methods=["GET"])
def service_info():
    # Spec: https://github.com/ga4gh-discovery/ga4gh-service-info
    return jsonify({
        "id": current_app.config["SERVICE_ID"],
        "name": SERVICE_NAME,
        "type": SERVICE_TYPE,
        "description": "Data repository service (based on GA4GH's specs) for a Bento platform node.",
        "organization": {
            "name": "C3G",
            "url": "http://c3g.ca"
        },
        "contactUrl": "mailto:simon.chenard2@mcgill.ca",
        "version": __version__,
    })


@drs_service.route("/objects/<string:object_id>", methods=["GET"])
def object_info(object_id):
    drs_bundle = DrsBundle.query.filter_by(id=object_id).first()
    drs_object = None

    if not drs_bundle:  # Only try hitting the database for an object if no bundle was found
        drs_object = DrsObject.query.filter_by(id=object_id).first()

        if not drs_object:
            return flask_errors.flask_not_found_error("No object found for this ID")

    # Are we inside the bento singularity container? if so, provide local accessmethod
    inside_container = request.headers.get("X-CHORD-Internal", "0") == "1"

    # Log X-CHORD-Internal header
    current_app.logger.info(
        f"[{SERVICE_NAME}] object_info X-CHORD-Internal: {request.headers.get('X-CHORD-Internal', 'not set')}"
    )

    if drs_bundle:
        response = build_bundle_json(drs_bundle, inside_container=inside_container)
    else:
        response = build_object_json(drs_object, inside_container=inside_container)

    return jsonify(response)


@drs_service.route("/search", methods=["GET"])
def object_search():
    response = []
    name = request.args.get("name")
    fuzzy_name = request.args.get("fuzzy_name")

    if name:
        objects = DrsObject.query.filter_by(name=name).all()
    elif fuzzy_name:
        objects = DrsObject.query.filter(DrsObject.name.contains(fuzzy_name)).all()
    else:
        return flask_errors.flask_bad_request_error("Missing GET search terms (either name or fuzzy_name)")

    for obj in objects:
        response.append(build_object_json(obj))

    return jsonify(response)


@drs_service.route("/objects/<string:object_id>/download", methods=["GET"])
def object_download(object_id):
    try:
        drs_object = DrsObject.query.filter_by(id=object_id).one()
    except NoResultFound:
        return flask_errors.flask_not_found_error("No object found for this ID")

    minio_obj = drs_object.return_minio_object()

    if not minio_obj:
        return send_file(drs_object.location)

    # TODO: kinda greasy, not really sure we want to support such a feature later on
    response = make_response(
        send_file(
            minio_obj["Body"],
            mimetype="application/octet-stream",
            as_attachment=True,
            attachment_filename=drs_object.name
        )
    )

    response.headers["Content-length"] = minio_obj["ContentLength"]
    return response


@drs_service.route("/private/ingest", methods=["POST"])
def object_ingest():
    data = request.json or {}

    obj_path: str = data.get("path")

    if not obj_path or not isinstance(obj_path, str):
        return flask_errors.flask_bad_request_error("Missing or invalid path parameter in JSON request")

    # TODO: Should this always be the case?
    deduplicate: bool = data.get("deduplicate", False)

    drs_object: Optional[DrsObject] = None
    if deduplicate:
        # Get checksum of original file, and query database for objects that match
        checksum = drs_file_checksum(obj_path)
        drs_object = DrsObject.query.filter_by(checksum=checksum).first()

    if not drs_object:
        try:
            drs_object = DrsObject(location=obj_path)

            db.session.add(drs_object)
            db.session.commit()
        except Exception as e:  # TODO: More specific handling
            current_app.logger.error(f"[{SERVICE_NAME}] Encountered exception during ingest: {e}")
            return flask_errors.flask_bad_request_error("Error while creating the object")

    response = build_object_json(drs_object)

    return response, 201

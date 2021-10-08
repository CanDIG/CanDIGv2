"""
Methods to handle incoming CNV service requests
"""
import datetime

import flask
import uuid

from sqlalchemy import exc, or_

from candig_cnv_service.orm import get_session, ORMException
from candig_cnv_service.orm.models import Patient, Sample, CNV
from candig_cnv_service import orm
from candig_cnv_service.api.logging import apilog, logger
from candig_cnv_service.api.logging import structured_log as struct_log
from candig_cnv_service.api.exceptions import IdentifierFormatError

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
    report = typename + " search failed"
    message = "Internal error searching for " + typename + "s"
    logger().error(
        struct_log(action=report, exception=str(exception), **kwargs)
    )
    return dict(message=message, code=500)


def _report_object_exists(typename, **kwargs):
    """
    Generate standard log message + request error for warning:
    Trying to POST an object that already exists
    :param typename: name of type involved
    :param **kwargs: arbitrary keyword parameters
    :return: Connexion Error() type to return
    """
    report = typename + " already exists"
    logger().warning(struct_log(action=report, **kwargs))
    return dict(message=report, code=400)


def _report_foreign_key(typename, **kwargs):
    """
    Generate standard log message + request error for warning:
    Trying to POST an object that lacks a foreign key
    :param typename: name of type involved
    :param **kwargs: arbitrary keyword parameters
    :return: Connexion Error() type to return
    """
    report = typename + " requires an existing foreign key"
    logger().warning(struct_log(action=report, **kwargs))
    return dict(message=report, code=400)


def _report_update_failed(typename, exception, **kwargs):
    """
    Generate standard log message + request error for error:
    Internal error performing update (PUT)
    :param typename: name of type involved
    :param exception: exception thrown by ORM
    :param **kwargs: arbitrary keyword parameters
    :return: Connexion Error() type to return
    """
    report = typename + " updated failed"
    message = "Internal error updating " + typename + "s"
    logger().error(
        struct_log(action=report, exception=str(exception), **kwargs)
    )
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
    report = "Could not convert " + typename + " to ORM model"
    message = typename + (
        ": failed validation - could not " "convert to internal representation"
    )
    logger().error(
        struct_log(action=report, exception=str(exception), **kwargs)
    )
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
    report = "Internal error writing " + typename + " to DB"
    message = typename + ": internal error saving ORM object to DB"
    logger().error(
        struct_log(action=report, exception=str(exception), **kwargs)
    )
    err = dict(message=message, code=500)
    return err


def get_patients():
    """
    Return all individuals
    """

    db_session = get_session()

    try:
        q = db_session.query(Patient)
    except orm.ORMException as e:
        err = _report_search_failed("patient", e, patient_id="all")
        return err, 500

    patient_ids_dict = [orm.dump(p) for p in q]
    return [d["patient_id"] for d in patient_ids_dict], 200


@apilog
def get_samples(patient_id, tags=None, description=None):
    """
    Return samples of a patient.

    :param patient_id: Id of patient
    :type patient_id = string
    :param tags: List of tags
    :type tags: list

    :returns: samples, 200 on sucess, error code on failure
    :rtype: object, int
    """

    db_session = get_session()

    if not patient_id:
        err = dict(message="No patient_id provided", code=400)
        return err, 400

    try:
        q = db_session.query(Sample).filter_by(patient_id=patient_id)

        if tags:
            q = q.filter(or_(*[Sample.tags.contains(tag) for tag in tags]))

        if description:
            q = q.filter(Sample.description.contains(description))

    except orm.ORMException as e:
        err = _report_search_failed("sample", e, patient_id=patient_id)
        return err, 500

    response = {}
    dump = [orm.dump(p) for p in q]
    for d in dump:
        response["patient_id"] = d["patient_id"]
        samples = response.get("samples", [])
        samples_dict = dict(sample_id=d["sample_id"])
        if d.get("tags"):
            samples_dict["tags"] = d["tags"]
        samples_dict["created"] = d["created"]
        samples_dict["description"] = d["description"]
        samples.append(samples_dict)
        response["samples"] = samples

    return response, 200


@apilog
def get_segments(
    patient_id, sample_id, chromosome_number, start_position, end_position
):
    """
    Return segments within the specified region

    :param: patient_id: Id of patient
    :type: string
    :param: sample_id: Id of sample
    :type: string
    :param: chromosome_number: Chromosome number
    :type: string
    :param: start_position: Start position
    :type: integer
    :param: end_position: End position
    :type: integer

    :returns: segments, 200 on sucess, error code on failure
    :rtype: object, int
    """

    db_session = get_session()
    try:
        validate_uuid_string("patient_id", str(patient_id))
    except IdentifierFormatError as e:
        err = _report_search_failed("cnv", e, patient_id=patient_id,)
        return err, 500

    if isinstance(sample_id, int):
        sample_id = str(sample_id)
    if isinstance(chromosome_number, int):
        chromosome_number = str(chromosome_number)

    try:
        q = (
            db_session.query(CNV)
            .join(Sample)
            .filter(
                CNV.chromosome_number == chromosome_number,
                Sample.sample_id == sample_id,
                Sample.patient_id == patient_id,
            )
        )
    except orm.ORMException as e:
        err = _report_search_failed(
            "cnv",
            e,
            patient_id=patient_id,
            sample_id=sample_id,
            chromosome_number=chromosome_number,
        )
        return err, 400

    response = []
    segments = [orm.dump(p) for p in q]
    for segment in segments:
        if (
            (
                segment["start_position"] >= start_position
                and segment["end_position"] <= end_position
            )
            or (
                segment["start_position"]
                <= start_position
                <= segment["end_position"]
            )
            or (
                segment["start_position"]
                <= end_position
                <= segment["end_position"]
            )
            or (
                start_position <= segment["start_position"]
                and segment["end_position"] <= end_position
            )
        ):
            del segment["sample_id"]
            response.append(segment)
    print(response)
    return response, 200


@apilog
def add_patients(body):
    """
    Creates a new patient following the Patient schema,
    only adding Patient level information.

    :param body: POST request body
    :type body: object

    :returns: message, 201 on success, error code on failure
    :rtype: object, int

    .. note::
        Refer to the OpenAPI Spec for a proper schemas of Patient objects.
    """

    db_session = get_session()

    try:
        orm_patient = Patient(patient_id=body.get("patient_id"))
    except TypeError as e:
        err = _report_conversion_error("patient", e, **body)
        return err, 400

    try:
        db_session.add(orm_patient)
        db_session.commit()
    except exc.IntegrityError:
        db_session.rollback()
        err = _report_object_exists("patient: " + body["patient_id"], **body)
        return err, 400
    except ORMException as e:
        db_session.rollback()
        err = _report_write_error("patient", e, **body)
        return err, 500

    return {"code": 201, "message": "Patient successfully added"}, 201


@apilog
def add_samples(body):
    """
    Creates a new sample following the Sample schema,
    only adding Sample level information.

    :param body: POST request body
    :type body: object

    :returns: message, 201 on success, error code on failure
    :rtype: object, int

    .. note::
        Refer to the OpenAPI Spec for a proper schemas of Sample objects.
    """

    db_session = get_session()

    print(body)

    if not body.get("patient_id"):
        err = dict(message="No patient_id provided", code=400)
        return err, 400

    if not body.get("sample_id"):
        err = dict(message="No sample_id provided", code=400)
        return err, 400

    if not body.get("description"):
        err = dict(message="No description provided", code=400)
        return err, 400

    body["created"] = datetime.datetime.utcnow()

    try:
        orm_sample = Sample(**body)
    except TypeError as e:
        err = _report_conversion_error("sample", e, **body)
        return err, 400

    try:
        db_session.add(orm_sample)
        db_session.commit()
    except exc.IntegrityError as ie:
        if ie.args[0].find("FOREIGN KEY constraint failed"):
            db_session.rollback()
            err = _report_foreign_key("sample: " + body["sample_id"], **body)
            return err, 400

        db_session.rollback()
        err = _report_object_exists("sample: " + body["sample_id"], **body)
        return err, 400
    except ORMException as e:
        db_session.rollback()
        err = _report_write_error("sample", e, **body)
        return err, 500

    return {"code": 201, "message": "Sample successfully added"}, 201


@apilog
def add_segments(body):
    """
    Creates a new CNV following the CNV schema attached to an
    existing sample.

    :param body: POST request body
    :type body: object

    :returns: message, 201 on success, error code on failure
    :rtype: object, int

    .. note::
        Refer to the OpenAPI Spec for a proper schemas of CNV objects.
    """

    db_session = get_session()

    if not body.get("patient_id"):
        err = dict(message="No patient_id provided", code=400)
        return err, 400

    if not body.get("sample_id"):
        err = dict(message="No sample_id provided", code=400)
        return err, 400

    segments = body["segments"]
    for segment in segments:
        segment["sample_id"] = body["sample_id"]
        print(segment)
        try:
            orm_segment = CNV(**segment)
        except TypeError as e:
            err = _report_conversion_error("segment", e, **body)
            return err, 400

        try:
            db_session.add(orm_segment)
            db_session.commit()
        except exc.IntegrityError as ie:
            if ie.args[0].find("FOREIGN KEY constraint failed"):
                db_session.rollback()
                err = _report_foreign_key(
                    "segment: " + body["sample_id"], **body
                )
                return err, 400

            db_session.rollback()
            err = _report_object_exists(
                "segment: " + body["sample_id"], **body
            )
            return err, 400
        except ORMException as e:
            db_session.rollback()
            err = _report_write_error("segment", e, **body)
            return err, 500

    return {"code": 201, "message": "Segments successfully added"}, 201


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

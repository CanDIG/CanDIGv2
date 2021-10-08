import string
import random
import uuid
import pytest
import os
import sys

sys.path.append("{}/{}".format(os.getcwd(), "candig_cnv_service"))
sys.path.append(os.getcwd())

from candig_cnv_service import orm
from candig_cnv_service.__main__ import app
from candig_cnv_service.api import operations


@pytest.fixture(name="test_client")
def load_test_client(db_filename="operations.db"):
    try:
        orm.close_session()
        os.remove(db_filename)
    except FileNotFoundError:
        pass
    except OSError:
        pass

    context = app.app.app_context()

    with context:
        orm.init_db("sqlite:///" + db_filename)
        app.app.config["BASE_DL_URL"] = "http://127.0.0.1"

    return context


def test_add_patients(test_client):
    """
    Test add_patients method
    """

    context = test_client
    patient_1, patient_2, patient_3 = load_test_patients()

    with context:
        response, code = operations.add_patients(patient_1)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_patients(patient_2)
        assert code == 201
        assert response["code"] == 201

        # Invalid 'patient_id'
        response, code = operations.add_patients(patient_3)
        assert code == 500
        assert response["code"] == 500


def test_add_same_patient(test_client):
    """
    Test adding same patient twice 
    """
    context = test_client
    patient_1, _, _ = load_test_patients()

    with context:
        response, code = operations.add_patients(patient_1)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_patients(patient_1)
        assert code == 400
        assert response["code"] == 400


def test_get_patient(test_client):
    """
    Test 'get_patient' method 
    """
    context = test_client
    patient_1, patient_2, _ = load_test_patients()

    with context:
        operations.add_patients(patient_1)
        operations.add_patients(patient_2)
        result, code = operations.get_patients()
        assert len(result) == 2
        assert code == 200

        assert patient_1["patient_id"] in result


def test_add_samples(test_client):
    """
    Test 'add_samples' method
    """
    context = test_client
    sample_1, sample_2, _, patient_1 = load_test_samples()

    with context:
        _, code = operations.add_patients(patient_1)
        assert code == 201

        response, code = operations.add_samples(sample_1)
        assert code == 201
        assert response["code"] == 201


def test_add_sample_twice(test_client):
    """
    Test adding the same sample twice
    """
    context = test_client
    sample_1, _, _, patient_1 = load_test_samples()

    with context:
        _, code = operations.add_patients(patient_1)
        assert code == 201

        response, code = operations.add_samples(sample_1)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_samples(sample_1)
        assert code == 400
        assert response["code"] == 400


def test_add_sample_no_patient(test_client):
    """
    Test adding sample where no patient information
    is present on patient table 
    """

    context = test_client
    _, _, sample, _ = load_test_samples()

    with context:
        response, code = operations.add_samples(sample)
        assert code == 400
        assert response["code"] == 400


def test_get_samples(test_client):
    """
    Test 'get_samples' method
    """

    context = test_client

    sample_1, sample_2, _, patient_1 = load_test_samples()
    sample_3, sample_4, _, patient_2 = load_test_samples()

    with context:
        _, code = operations.add_patients(patient_1)
        assert code == 201
        _, code = operations.add_patients(patient_2)
        assert code == 201

        _, code = operations.add_samples(sample_1)
        assert code == 201
        _, code = operations.add_samples(sample_2)
        assert code == 201

        _, code = operations.add_samples(sample_3)
        assert code == 201
        _, code = operations.add_samples(sample_4)
        assert code == 201

        response, code = operations.get_samples(patient_1["patient_id"])
        samples = [s["sample_id"] for s in response["samples"]]
        descriptions = [s["description"] for s in response["samples"]]
        assert code == 200
        assert len(samples) == 2
        assert sample_1["sample_id"] in samples
        assert sample_1["description"] in descriptions
        assert sample_2["sample_id"] in samples
        assert sample_2["description"] in descriptions
       

def test_get_samples_using_description(test_client):
    """
    Test 'get_samples' method using a description
    """

    context = test_client

    sample_1, sample_2, _, patient_1 = load_test_samples()
    sample_3, sample_4, _, patient_2 = load_test_samples()

    with context:
        _, code = operations.add_patients(patient_1)
        assert code == 201
        _, code = operations.add_patients(patient_2)
        assert code == 201

        _, code = operations.add_samples(sample_1)
        assert code == 201
        _, code = operations.add_samples(sample_2)
        assert code == 201

        _, code = operations.add_samples(sample_3)
        assert code == 201
        _, code = operations.add_samples(sample_4)
        assert code == 201

        response, code = operations.get_samples(patient_1["patient_id"], description=sample_1["description"])
        assert code == 200
        assert response["patient_id"] == sample_1["patient_id"] 


def test_add_samples_with_tags(test_client):
    """
    Test adding samples with tags
    """
    context = test_client
    sample_1, sample_2, patient_1 = load_test_samples_with_tags()

    with context:
        _, code = operations.add_patients(patient_1)
        assert code == 201

        _, code = operations.add_samples(sample_1)
        assert code == 201
        _, code = operations.add_samples(sample_2)
        assert code == 201

def test_add_samples_no_description(test_client):
    """
    Test adding sample with missing description
    """
    context = test_client
    sample_1, _, _, patient_1 = load_test_samples()
    del sample_1["description"]
 
    with context:
        _, code = operations.add_patients(patient_1)
        assert code == 201

        response, code = operations.add_samples(sample_1)
        assert code == 400
        assert response["code"] == 400    

def test_get_samples_with_tags(test_client):
    """
    Test 'get_samples' using tags
    """
    context = test_client
    sample_1, sample_2, patient_1 = load_test_samples_with_tags()
    patient_id = patient_1["patient_id"]
    tags = sample_1["tags"]

    with context:
        _, code = operations.add_patients(patient_1)
        assert code == 201

        _, code = operations.add_samples(sample_1)
        assert code == 201
        _, code = operations.add_samples(sample_2)
        assert code == 201

        response, code = operations.get_samples(patient_id, tags)
        assert code == 200
        assert response["patient_id"] == patient_id
        assert len(response["samples"]) == 2

        response, code = operations.get_samples(patient_id, ["Adult"])
        assert code == 200
        assert response["patient_id"] == patient_id
        assert len(response["samples"]) == 1

        response, code = operations.get_samples(
            patient_id, ["Non existent tag"]
        )
        assert code == 200
        assert not response


def test_get_samples_invalid_patient_id(test_client):
    """
    Test 'get_samples' when patient_id values are invalid
    """
    context = test_client
    sample_1, sample_2, _, patient_1 = load_test_samples()
    _, _, _, patient_2 = load_test_samples()

    with context:
        _, code = operations.add_patients(patient_1)
        assert code == 201

        _, code = operations.add_samples(sample_1)
        assert code == 201
        _, code = operations.add_samples(sample_2)
        assert code == 201

        _, code = operations.add_patients(patient_2)
        assert code == 201

        response, code = operations.get_samples(patient_2["patient_id"])
        assert code == 200
        assert not response


def test_add_segments(test_client):
    """
    Test 'add_segments' method
    """

    context = test_client

    patient, sample, segment, _, _ = load_test_segment()

    with context:
        response, code = operations.add_patients(patient)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_samples(sample)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_segments(segment)
        assert code == 201
        assert response["code"] == 201


def test_add_segments_no_sample(test_client):
    """
    Test 'add_segments' method when sample is not provided
    """

    context = test_client

    patient, sample, segment, _, _ = load_test_segment()

    segment["sample_id"] = ""

    with context:
        response, code = operations.add_patients(patient)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_samples(sample)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_segments(segment)
        assert code == 400
        assert response["code"] == 400


def test_add_segment_no_patient(test_client):
    """
    Test "add_segment" method when patient is not provided
    """

    context = test_client

    patient, sample, segment, _, _ = load_test_segment()

    segment["patient_id"] = ""

    with context:
        response, code = operations.add_patients(patient)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_samples(sample)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_segments(segment)
        assert code == 400
        assert response["code"] == 400


def test_add_segments_twice(test_client):
    """
    Test 'add_segments' method adding the same segment twice
    """
    context = test_client

    patient, sample, segment, _, _ = load_test_segment()

    with context:
        response, code = operations.add_patients(patient)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_samples(sample)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_segments(segment)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_segments(segment)
        assert code == 400
        assert response["code"] == 400


def test_get_segment(test_client):
    """
    Test 'get_segments' method
    """

    context = test_client

    patient_1, sample_1, segment_1, segment_2, segment_3 = load_test_segment()
    patient_2, sample_2, segment_4, segment_5, segment_6 = load_test_segment()

    patient_id = segment_1["patient_id"]
    sample_id = segment_1["sample_id"]
    chromosome_number = segment_1["segments"][0]["chromosome_number"]
    start_position = segment_1["segments"][0]["start_position"]
    end_position = segment_1["segments"][0]["end_position"]
    copy_number = segment_1["segments"][0]["copy_number"]
    copy_number_ploidy_corrected = segment_1["segments"][0][
        "copy_number_ploidy_corrected"
    ]

    with context:
        response, code = operations.add_patients(patient_1)
        assert code == 201
        assert response["code"] == 201
        response, code = operations.add_patients(patient_2)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_samples(sample_1)
        assert code == 201
        assert response["code"] == 201
        response, code = operations.add_samples(sample_2)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_segments(segment_1)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_segments(segment_2)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_segments(segment_3)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_segments(segment_4)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_segments(segment_5)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_segments(segment_6)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.get_segments(
            patient_id,
            sample_id,
            chromosome_number,
            start_position,
            end_position,
        )
        assert len(response) == 1
        assert code == 200

        assert response[0]["chromosome_number"] == chromosome_number
        assert response[0]["start_position"] == start_position
        assert response[0]["end_position"] == end_position
        assert response[0]["copy_number"] == copy_number
        assert (
            response[0]["copy_number_ploidy_corrected"]
            == copy_number_ploidy_corrected
        )

        response, code = operations.get_segments(
            patient_id,
            sample_id,
            chromosome_number,
            start_position=12522,
            end_position=34326,
        )
        
        assert code == 200
        assert len(response) == 2


def test_get_segments_invalid_data(test_client):
    """
    Test 'get_segments' using invalid or non-existent data
    """
    context = test_client

    patient_id = 1
    sample_id = 2
    chromosome_number = 3
    start_position = 4
    end_position = 5

    with context:
        response, code = operations.get_segments(
            patient_id,
            sample_id,
            chromosome_number,
            start_position,
            end_position,
        )
        assert response["code"] == 500
        assert code == 500


def load_test_patients():
    """
    Load some mock patient data
    """
    patient_1_id = uuid.uuid4().hex
    patient_2_id = uuid.uuid4().hex
    patient_3_id = 1

    test_patient_1 = {
        "patient_id": patient_1_id,
    }

    test_patient_2 = {
        "patient_id": patient_2_id,
    }

    test_patient_3 = {
        "patient_id": patient_3_id,
    }

    return test_patient_1, test_patient_2, test_patient_3


def load_test_samples():
    """
    Return some mock sample data
    """
    samp = lambda x: "".join(
        random.choice(string.ascii_lowercase) for i in range(x)
    )

    patient_1, _, _ = load_test_patients()

    sample_1 = {"sample_id": samp(5), "patient_id": patient_1["patient_id"], "description": patient_1["patient_id"] + "sample_1"}

    sample_2 = {"sample_id": samp(5), "patient_id": patient_1["patient_id"], "description": patient_1["patient_id"] + "sample_2"}

    sample_3 = {"sample_id": samp(5)}

    return sample_1, sample_2, sample_3, patient_1


def load_test_samples_with_tags():
    """
    Return some mock sample data with tags
    """
    samp = lambda x: "".join(
        random.choice(string.ascii_lowercase) for i in range(x)
    )

    patient_1, _, _ = load_test_patients()

    sample_1 = {
        "sample_id": samp(5),
        "patient_id": patient_1["patient_id"],
        "tags": ["Canadian", "Ovarian"],
        "description": "sample_1",
    }

    sample_2 = {
        "sample_id": samp(5),
        "patient_id": patient_1["patient_id"],
        "tags": ["Canadian", "Liver", "Adult"],
        "description": "sample_2",
    }

    return sample_1, sample_2, patient_1


def load_test_segment():
    """
    Return some mock segments data
    """

    sample_1, _, _, patient_1 = load_test_samples()

    segment_1 = {
        "patient_id": patient_1["patient_id"],
        "sample_id": sample_1["sample_id"],
        "segments": [
            {
                "chromosome_number": "5",
                "start_position": 12523,
                "end_position": 23425,
                "copy_number": -0.16,
                "copy_number_ploidy_corrected": 0,
            }
        ],
    }

    segment_2 = {
        "patient_id": patient_1["patient_id"],
        "sample_id": sample_1["sample_id"],
        "segments": [
            {
                "chromosome_number": "5",
                "start_position": 23426,
                "end_position": 34326,
                "copy_number": -0.16,
                "copy_number_ploidy_corrected": 0,
            }
        ],
    }

    segment_3 = {
        "patient_id": patient_1["patient_id"],
        "sample_id": sample_1["sample_id"],
        "segments": [
            {
                "chromosome_number": "5",
                "start_position": 34327,
                "end_position": 44296,
                "copy_number": -0.16,
                "copy_number_ploidy_corrected": 0,
            }
        ],
    }

    return patient_1, sample_1, segment_1, segment_2, segment_3

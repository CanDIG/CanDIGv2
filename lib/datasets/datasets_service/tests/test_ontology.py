"""
Test suite to unit test ontology parsing (DUO for now)
"""

import uuid
import os
import sys
import pytest

sys.path.append("{}/{}".format(os.getcwd(), "candig_dataset_service"))
sys.path.append(os.getcwd())

from candig_dataset_service.ontologies.duo import OntologyParser, OntologyValidator, ont

duo = {
    1: "DUO:0000001", 2: "DUO:0000002", 3: "DUO:0000003", 4: "DUO:0000004",
    5: "DUO:0000005", 6: "DUO:0000006", 7: "DUO:0000007", 11: "DUO:0000011",
    12: "DUO:0000012", 14: "DUO:0000014", 15: "DUO:0000015", 16: "DUO:0000016",
    17: "DUO:0000017", 18: "DUO:0000018", 19: "DUO:0000019", 20: "DUO:0000020",
    21: "DUO:0000021", 22: "DUO:0000022", 24: "DUO:0000024", 25: "DUO:0000025",
    26: "DUO:0000026", 27: "DUO:0000027", 28: "DUO:0000028", 29: "DUO:0000029",
    31: "DUO:0000031", 32: "DUO:0000032", 33: "DUO:0000033", 34: "DUO:0000034",
    35: "DUO:0000035", 36: "DUO:0000036", 37: "DUO:0000037", 38: "DUO:0000038",
    39: "DUO:0000039", 40: "DUO:0000040", 42: "DUO:0000042"
}


[
    "DUO:0000001", "DUO:0000002", "DUO:0000003", "DUO:0000004",
    "DUO:0000005", "DUO:0000006", "DUO:0000007", "DUO:0000011",
    "DUO:0000012", "DUO:0000014", "DUO:0000015", "DUO:0000016",
    "DUO:0000017", "DUO:0000018", "DUO:0000019", "DUO:0000020",
    "DUO:0000021", "DUO:0000022", "DUO:0000024", "DUO:0000025",
    "DUO:0000026", "DUO:0000027", "DUO:0000028", "DUO:0000029",
    "DUO:0000042"
]




def test_valid_duo_000001():
    term = {"duo": [{"id": duo[1]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000002():
    term = {"duo": [{"id": duo[2]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()

    assert not valid



def test_valid_duo_000003():
    term = {"duo": [{"id": duo[3]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()

    assert not valid



def test_valid_duo_000004():
    term = {"duo": [{"id": duo[4]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000005():
    term = {"duo": [{"id": duo[5]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000006():
    term = {"duo": [{"id": duo[6]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000007():
    term = {"duo": [{"id": duo[7]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000011():
    term = {"duo": [{"id": duo[11]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000012():
    term = {"duo": [{"id": duo[12]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000014():
    term = {"duo": [{"id": duo[14]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000015():
    term = {"duo": [{"id": duo[15]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000016():
    term = {"duo": [{"id": duo[16]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000017():
    term = {"duo": [{"id": duo[17]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000018():
    term = {"duo": [{"id": duo[18]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000019():
    term = {"duo": [{"id": duo[19]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000020():
    term = {"duo": [{"id": duo[20]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000021():
    term = {"duo": [{"id": duo[21]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_not_implemented_duo_000022():
    term = {"duo": [{"id": duo[22]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert not valid
    assert invalid[0][duo[22]] == "Not currently supported"


def test_valid_duo_000024():
    term = {"duo": [{"id": duo[24], "modifier": "2030-01-01"}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_invalid_duo_000024():
    term = {"duo": [{"id": duo[24]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert not valid


def test_not_implemented_duo_000025():
    term = {"duo": [{"id": duo[25]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert not valid
    assert invalid[0][duo[25]] == "Not currently supported"


def test_valid_duo_000026():
    term = {"duo": [{"id": duo[26]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000027():
    term = {"duo": [{"id": duo[27]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000028():
    term = {"duo": [{"id": duo[28]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


def test_valid_duo_000029():
    term = {"duo": [{"id": duo[29]}]}
    ov = OntologyValidator(ont=ont, input_json=term)
    valid, invalid = ov.validate_duo()
    assert valid


# def test_valid_duo_000031():
#     term = {"duo": [{"id": duo[31]}]}
#     ov = OntologyValidator(ont=ont, input_json=term)
#     valid, invalid = ov.validate_duo()
#     assert valid

#
# def test_valid_duo_000032():
#     term = {"duo": [{"id": duo[32]}]}
#     ov = OntologyValidator(ont=ont, input_json=term)
#     valid, invalid = ov.validate_duo()
#     assert valid
#
#
# def test_valid_duo_000033():
#     term = {"duo": [{"id": duo[33]}]}
#     ov = OntologyValidator(ont=ont, input_json=term)
#     valid, invalid = ov.validate_duo()
#     assert valid
#
#
# def test_valid_duo_000034():
#     term = {"duo": [{"id": duo[34]}]}
#     ov = OntologyValidator(ont=ont, input_json=term)
#     valid, invalid = ov.validate_duo()
#     assert valid
#
#
# def test_valid_duo_000035():
#     term = {"duo": [{"id": duo[35]}]}
#     ov = OntologyValidator(ont=ont, input_json=term)
#     valid, invalid = ov.validate_duo()
#     assert valid
#
#
# def test_valid_duo_000036():
#     term = {"duo": [{"id": duo[36]}]}
#     ov = OntologyValidator(ont=ont, input_json=term)
#     valid, invalid = ov.validate_duo()
#     assert valid
#
#
# def test_valid_duo_000037():
#     term = {"duo": [{"id": duo[37]}]}
#     ov = OntologyValidator(ont=ont, input_json=term)
#     valid, invalid = ov.validate_duo()
#     assert valid
#
#
# def test_valid_duo_000038():
#     term = {"duo": [{"id": duo[38]}]}
#     ov = OntologyValidator(ont=ont, input_json=term)
#     valid, invalid = ov.validate_duo()
#     assert valid
#
#
# def test_valid_duo_000039():
#     term = {"duo": [{"id": duo[39]}]}
#     ov = OntologyValidator(ont=ont, input_json=term)
#     valid, invalid = ov.validate_duo()
#     assert valid
#
#
# def test_valid_duo_000040():
#     term = {"duo": [{"id": duo[40]}]}
#     ov = OntologyValidator(ont=ont, input_json=term)
#     valid, invalid = ov.validate_duo()
#     assert valid
#
#
# def test_valid_duo_000042():
#     term = {"duo": [{"id": duo[42]}]}
#     ov = OntologyValidator(ont=ont, input_json=term)
#     valid, invalid = ov.validate_duo()
#     assert valid
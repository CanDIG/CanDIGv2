"""
Test suite to check for errors upon federation_service start up
"""


import sys
import os
import logging

import pytest

sys.path.append("{}/{}".format(os.getcwd(), "candig_federation"))

sys.path.append(os.getcwd())

from candig_federation.api import network
from jsonschema.exceptions import ValidationError

VALID_PEERS = "./tests/test_data/peers.json"
INVALID_PEER_VAL = "./tests/test_data/peers_bad_value.json"
INVALID_PEER_KEY = "./tests/test_data/peers_bad_initkey.json"

VALID_SCHEMA = "./tests/test_data/schemas.json"
INVALID_SCHEMA = "notschemas"


def test_invalid_schema_location_getSchemaDict_exception():
    with pytest.raises(FileNotFoundError):
        network.get_schema_dict(INVALID_SCHEMA)

def test_invalid_schema_location_getSchemaDict_exit():
    with pytest.raises(SystemExit):
        network.get_schema_dict(INVALID_SCHEMA, logging.getLogger("Test"))

def test_invalid_schema_type_parseConfigs():
    with pytest.raises(KeyError):
        network.parse_configs("wrong", VALID_PEERS, VALID_SCHEMA)

def test_invalid_file_path_parseConfigs():
    with pytest.raises(FileNotFoundError):
        network.parse_configs("peers", "blank", VALID_SCHEMA)

def test_invalid_schema_format_value_parseConfigs():
    with pytest.raises(ValidationError):
        network.parse_configs("peers", INVALID_PEER_VAL, VALID_SCHEMA)

def test_invalid_schema_format_initkey_parseConfigs():
    with pytest.raises(KeyError):
        network.parse_configs("peers", INVALID_PEER_KEY, VALID_SCHEMA)

def test_invalid_schema_type_parseConfigs_exit():
    with pytest.raises(SystemExit):
        network.parse_configs("wrong", VALID_PEERS, VALID_SCHEMA, logging.getLogger("Test"))

def test_invalid_file_path_parseConfigs_exit():
    with pytest.raises(SystemExit):
        network.parse_configs("peers", "blank", VALID_SCHEMA, logging.getLogger("Test"))

def test_invalid_schema_format_value_parseConfigs_exit():
    with pytest.raises(SystemExit):
        network.parse_configs("peers", INVALID_PEER_VAL, VALID_SCHEMA, logging.getLogger("Test"))

def test_invalid_schema_format_initkey_parseConfigs_exit():
    with pytest.raises(SystemExit):
        network.parse_configs("peers", INVALID_PEER_KEY, VALID_SCHEMA, logging.getLogger("Test"))

def test_valid_schema_location_getSchemaDict():
    schema_dict = network.get_schema_dict(VALID_SCHEMA)
    assert [*schema_dict] == ['peers', 'services']

def test_valid_schema_parseConfigs():
    peers = network.parse_configs("peers", VALID_PEERS, VALID_SCHEMA)
    assert peers["p1"] == "http://10.9.208.132:8890"
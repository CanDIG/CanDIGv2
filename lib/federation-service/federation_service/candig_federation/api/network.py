"""
Provides parsing methods to initialize the server's peer to peer/service connections.
"""

import os
import json
import jsonschema


def parse_configs(schema_type, file_path, schema_path, logger=None):
    """
    Attempts to get a dict of peers/services from a json file specified in configuration.
    This file should have a json structure matching the schema specified.

    """
    schema_dict = get_schema_dict(schema_path, logger)

    # TODO Further Schema Validation for URLS

    try:
        if schema_type not in schema_dict.keys():
            raise KeyError
        else:
            with open(file_path) as json_file:
                data = json.load(json_file)
                jsonschema.validate(data, schema=schema_dict[schema_type])
                return data[schema_type]
    except FileNotFoundError:
        if logger:
            logger.warning("Couldn't load the "
                           "{} pairings. Try adding a "
                           "file named 'peers.json' "
                           "to {}/configs".
                           format(schema_type, os.getcwd()))
            exit()
        else:
            raise FileNotFoundError
    except jsonschema.ValidationError:
        if logger:
            logger.warning("{} object in {} "
                           "did not validate against the"
                           "schema. Please recheck file.".
                           format(schema_type, file_path))
            exit()
        else:
            raise jsonschema.ValidationError("{} object in {} "
                                             "did not validate against the"
                                             "schema. Please recheck file.".
                                             format(schema_type, file_path))
    except KeyError:
        if logger:
            logger.warning("{} not in known schemas. "
                           "Please check spelling in __main__.py "
                           "or add the schema".
                           format(schema_type))
            exit()
        else:
            raise KeyError


def get_schema_dict(file_path, logger=None):
    """
    Constructs a python dictonary from supplied schema in ./configs/file_path

    """
    try:
        with open(file_path) as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        if logger:
            logger.warning("Unable to find schema file. "
                           "Please check spelling or place "
                           "a 'schemas.json' at "
                           "{}/configs".format(os.getcwd()))
            exit()
        else:
            raise FileNotFoundError

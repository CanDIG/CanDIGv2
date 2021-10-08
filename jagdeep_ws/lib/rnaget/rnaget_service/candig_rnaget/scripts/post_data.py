#!/usr/bin/env python3
"""
Script for ingesting expression data to service
"""

import sys
import argparse
import requests
import os
import json

from candig_rnaget.api.operations import validate_uuid_string
from candig_rnaget.api.exceptions import AuthorizationError


def add_expression_file(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser('Upload an RNAGET expression file')

    # required arguments
    parser.add_argument('--url', required=True)  # e.g. https://candig.bcgsc.ca/rnaget
    parser.add_argument('--token', required=True)
    parser.add_argument('--file', required=True)
    parser.add_argument('--studyID', required=True)

    # optional arguments
    parser.add_argument('--tags')

    args = parser.parse_args(args)

    validate_uuid_string('studyID', args.studyID)

    headers = {
        'Content-type': 'application/json',
        'api_key': args.token
    }

    get_study = requests.get(
        url=args.url+'/studies/'+args.studyID,
        headers=headers
    )

    if get_study.status_code == 200:
        expression_obj = {}
        if args.tags:
            expression_obj['tags'] = args.tags.split(',')

        expression_obj['studyID'] = args.studyID
        expression_obj['fileType'] = "h5"

        if not os.path.exists(args.file):
            raise FileNotFoundError
        elif not args.file.endswith("h5"):
            raise TypeError("Expression file must be .h5")
        else:
            expression_obj['__filepath__'] = args.file

    elif get_study.status_code == 403:
        raise AuthorizationError
    else:
        raise Exception(
            "{} error running GET on study ID".format(get_study.status_code)
        )

    post_file = requests.post(
        url=args.url+'/expressions',
        data=json.dumps(expression_obj),
        headers=headers
    )

    if post_file.status_code == 201:
        print({
            'created': post_file.json()['created'],
            'id': post_file.json()['id']
        })

    elif post_file.status_code == 403:
        raise AuthorizationError

    else:
        raise Exception(
            "{} error while making POST request".format(post_file.status_code)
        )


if __name__ == "__main__":
    add_expression_file()

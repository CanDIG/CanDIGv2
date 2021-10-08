#!/usr/bin/env python3
"""
Script for ingesting study data to service
"""

import sys
import argparse
import requests
import json

from candig_rnaget.api.operations import validate_uuid_string
from candig_rnaget.api.exceptions import AuthorizationError


def add_study(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser('Create an RNAGET study record')

    # required arguments
    parser.add_argument('--url', required=True)  # e.g. https://candig.bcgsc.ca/rnaget
    parser.add_argument('--token', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--projectID', required=True)

    # optional arguments
    parser.add_argument('--tags')
    parser.add_argument('--description')
    parser.add_argument('--sampleList')
    parser.add_argument('--patientList')

    args = parser.parse_args(args)

    validate_uuid_string('projectID', args.projectID)

    headers = {
        'Content-type': 'application/json',
        'api_key': args.token
    }

    get_project = requests.get(
        url=args.url+'/projects/'+args.projectID,
        headers=headers
    )

    if get_project.status_code == 200:
        study_obj = {
            'name': args.name,
            'parentProjectID': args.projectID
        }

        if args.tags:
            study_obj['tags'] = args.tags.split(',')
        if args.sampleList:
            study_obj['sampleList'] = args.sampleList.split(',')
        if args.patientList:
            study_obj['patientList'] = args.patientList.split(',')
        if args.description:
            study_obj['description'] = args.description

    elif get_project.status_code == 403:
        raise AuthorizationError
    else:
        raise Exception(
            "{} error running GET on project ID".format(get_project.status_code)
        )

    post_study = requests.post(
        url=args.url+'/studies',
        data=json.dumps(study_obj),
        headers=headers
    )

    if post_study.status_code == 201:
        print({
            'created': post_study.json()['created'],
            'id': post_study.json()['id']
        })
    elif post_study.status_code == 403:
        raise AuthorizationError
    else:
        raise Exception(
            "{} error while making POST request".format(post_study.status_code)
        )


if __name__ == "__main__":
    add_study()

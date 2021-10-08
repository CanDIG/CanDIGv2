#!/usr/bin/env python3
"""
Script for ingesting project data to service
"""

import sys
import argparse
import requests
import json

from candig_rnaget.api.exceptions import AuthorizationError


def add_project(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser('Create an RNAGET project record')

    # required arguments
    parser.add_argument('--url', required=True)  # e.g. https://candig.bcgsc.ca/rnaget
    parser.add_argument('--token', required=True)
    parser.add_argument('--name', required=True)

    # optional arguments
    parser.add_argument('--tags')
    parser.add_argument('--description')

    args = parser.parse_args(args)

    headers = {
        'Content-type': 'application/json',
        'api_key': args.token
    }

    project_obj = {'name': args.name}

    if args.tags:
        project_obj['tags'] = args.tags.split(',')
    if args.description:
        project_obj['description'] = args.description

    post_project = requests.post(
        url=args.url+'/projects',
        data=json.dumps(project_obj),
        headers=headers
    )

    if post_project.status_code == 201:
        print({
            'created': post_project.json()['created'],
            'id': post_project.json()['id']
        })
    elif post_project.status_code == 403:
        raise AuthorizationError
    else:
        raise Exception(
            "{} error while making POST request".format(post_project.status_code)
        )


if __name__ == "__main__":
    add_project()

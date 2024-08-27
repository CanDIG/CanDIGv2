#!/usr/bin/env python3

import argparse
import requests
import time
from threading import Thread

parser = argparse.ArgumentParser(
    prog="Endpoint stress-tester",
    description="""
Floods a given URL with requests, ensuring that the return is
consistent"""
    )
parser.add_argument(
    '--url',
    help='URL to hit',
    required=True
    )
parser.add_argument(
    '--expected-response',
    help='A file containing the expected response',
    required=True,
    type=argparse.FileType('r')
    )
parser.add_argument(
    '-X',
    help='HTTP type (GET or POST)',
    required=False,
    default="get"
    )
parser.add_argument(
    '-n',
    help='Number of iterations to test with',
    required=False,
    default=100000
)
parser.add_argument(
    '-H',
    '--headers',
    help='Header to use',
    required=False,
    default=100000
)


def make_single_request(is_post, url, headers, expected_response, invalid_returns, timings):
    start = time.time()
    response = ""
    if is_post:
        response = requests.post(url, headers=headers)
    else:
        response = requests.get(url, headers=headers)
    end = time.time()
    timings.append(end - start)
    if not response.ok or response.text != expected_response:
        invalid_returns.append(response)


def stress_test():
    args = parser.parse_args()
    is_post = args.X.lower() == "post"
    expected_response = args.expected_response.read()

    # Parse out headers into an object
    headers = {}
    invalid_returns = []
    all_threads = []
    timings = []
    for _ in range(args.n):
        t = Thread(target=make_single_request,args=(is_post, args.url, headers, expected_response, invalid_returns, timings))
        t.run()
        all_threads.append(t)
    

if __name__ == "__main__":
    stress_test()

#!/usr/bin/env python3

import argparse
import re
import requests
import threading
import time

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
    '-X',
    help='HTTP type (GET or POST)',
    required=False,
    default="get"
    )
parser.add_argument(
    '-n',
    help='Number of iterations to test with',
    required=False,
    default=100000,
    type=int
)
parser.add_argument(
    '-H',
    '--headers',
    help='Header to use',
    required=False,
    nargs='*'
)


def make_single_request(is_post, url, headers, expected_response, invalid_returns, timings, response_lock):
    start = time.time()
    response = ""
    if is_post:
        response = requests.post(url, headers=headers)
    else:
        response = requests.get(url, headers=headers)
    end = time.time()
    response_lock.acquire()
    timings.append(end - start)
    if not response.ok or response.text != expected_response:
        invalid_returns.append(response)
    response_lock.release()


def stress_test():
    # Parse out args
    args = parser.parse_args()
    is_post = args.X.lower() == "post"

    headers = {}
    for header in args.headers:
        split_header = header.split(": ", 1)
        headers[split_header[0]] = split_header[1]

    url = args.url
    if not re.search(r':\/\/', url):
        url = 'http://' + url

    # Poll once to see what the endpoint returns
    if is_post:
        response = requests.post(url, headers=headers)
    else:
        response = requests.get(url, headers=headers)

    if not response.ok:
        print(f"Error while trying the endpoint once: {response.status_code} {response.reason}")
        return

    # Check with the user to make sure the response seems ok
    user_ok = ""
    while user_ok != "y":
        print(f"Response: \n{response.text}\n\nDoes this look ok? (y/n)")
        user_ok = input().lower()
        if user_ok == "n":
            return
        elif user_ok != "y":
            print("Sorry, I didn't understand that. Please enter either y or n")
    expected_response = response.text

    # Start all the threads
    invalid_returns = []
    all_threads = []
    timings = []
    response_lock = threading.Lock()
    for _ in range(args.n):
        t = threading.Thread(target=make_single_request,args=(is_post, url, headers, expected_response, invalid_returns, timings, response_lock))
        t.start()
        all_threads.append(t)

    # Run through the list of threads until all of them are complete
    for thread in all_threads:
        thread.join()

    # Check the average response time
    lowest = min(timings)
    highest = max(timings)
    print(f"Shortest response: {lowest}s\nLongest response: {highest}s\nInvalid responses: {len(invalid_returns)}")
    if len(invalid_returns) > 0:
        print(f"\nSample invalid response: {invalid_returns[0]}")


if __name__ == "__main__":
    stress_test()

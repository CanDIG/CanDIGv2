"""
MockResponse: Functions like a regular Response from Requests
MockResponseInternal: Responses which are accessed in within handle_peer_requests
    have already been modified by the time they are received.
"""

import json

class MockResponse:
    def __init__(self, json_data, status_code, headers={}):
        self.json_data = json_data
        self.status_code = status_code
        self.headers = {'X-Source': '2222'}

    def json(self):
        return self.json_data

    def status_code(self):
        return self.status_code

    def headers(self):
        return self.headers


# Internal Response needs a result() function since it's supposed to be a Future response

class MockResponseInternal:
    def __init__(self, json_data, status_code, headers={}):
        self.json_data = json_data
        self.status_code = status_code
        self.headers = {'X-Source': '2222'}


    def json(self):
        return {"results": self.json_data,
                "status": self.status_code}
    
    def headers(self):
        return self.headers

    def result(self):
        return MockResponseInternal(self.json_data, self.status_code)


class testHeader():
    def __init__(self, headers):
        self.headers = headers

    def headers(self):
        return self.headers


TWO = {
    "p1": "http://10.9.208.132:6000",
    "p2": "http://10.9.208.132:8000"
}
THREE = {
    "p1": "http://10.9.208.132:6000",
    "p2": "http://10.9.208.132:8000",
    "p3": "http://10.9.208.132:9000"
}


exampleHeaders = testHeader({
        "Content-Type": "application/json",
        "Host": "ga4ghdev01.bcgsc.ca:8890",
        "User-Agent": "python-requests/2.22.0",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsI",
        "Federation": "false"
    })

fedHeader = testHeader({
        "Content-Type": "application/json",
        "Host": "ga4ghdev01.bcgsc.ca:8890",
        "User-Agent": "python-requests/2.22.0",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsI",
        "Federation": "true"
    })



TP = {
    "URI": "10.9.208.132",
    "PORT0": "8890",
    "PORT1": "8891",
    "PORT2": "8892",
    "Headers": exampleHeaders,
    "Federate": fedHeader,
    "Tyk1": "10.9.208.132:6000",
    "Tyk2": "10.9.208.132:8000",
    "Tyk3": "10.9.208.132:9000",
    "path": "rnaget/projects",
    "service": "TestService",

}

AP = {
    "s1": MockResponse([{"projects": {"k1": "v1", "k2": "v2"}}], 200),
    "s2": MockResponse([{"projects": {"key1": "value1"}}], 200),
    "s3": MockResponse([{"projects": {"keyA": "valueB"}}], 200),
    "i1": MockResponseInternal([{"projects": {"k1": "v1", "k2": "v2"}}], 200),
    "i2": MockResponseInternal([{"projects": {"key1": "value1"}}], 200),
    "i3": MockResponseInternal([{"projects": {"keyA": "valueB"}}], 200),
    "timeout": MockResponseInternal({}, 408),
    "fail": MockResponse(None, 404),
    "v1": {"projects": {"k1": "v1", "k2": "v2"}},
    "v2": {"projects": {"key1": "value1"}},
    "v3": {"projects": {"keyA": "valueB"}},
}



PostListM1 = {
    "data": [
        {
            "id": "WytHH1",
            "name": "mock1",
            "desc": "METADATA SERVER"
        },
        {
            "id": "WytHH2",
            "name": "mock2",
            "desc": "METADATA SERVER"
        }
    ]
}


PostListV1 = {
    "data": [
        {
            "id": "PLVE11",
            "name": "mockV11",
            "desc": "VARIANT SERVER"
        },
        {
            "id": "PLVE12",
            "name": "mockV12",
            "desc": "VARIANT SERVER"
        }
    ]
}

PostListV2 = {
    "data": [
        {
            "id": "PLVE21",
            "name": "mockV21",
            "desc": "VARIANT SERVER"
        },
        {
            "id": "PLVE22",
            "name": "mockV22",
            "desc": "VARIANT SERVER"
        }
    ]
}

PostListV3 = {
    "data": [
        {
            "id": "PLVE31",
            "name": "mockV31",
            "desc": "VARIANT SERVER"
        },
        {
            "id": "PLVE32",
            "name": "mockV32",
            "desc": "VARIANT SERVER"
        }
    ]
}

PR = {
    "PLM1": MockResponse([PostListM1], 200),
    "PLV1": MockResponse([PostListV1], 200),
    "PLV2": MockResponse([PostListV2], 200),
    "iPLV1": MockResponseInternal([PostListV1], 200),
    "iPLV2": MockResponseInternal([PostListV2], 200),
    "PLV3": MockResponse([PostListV3], 200),
    "iPLV3": MockResponseInternal([PostListV3], 200)
}


"""

Provides methods to handle both local and federated requests
"""


import json
import requests
from flask import current_app
from requests_futures.sessions import FuturesSession

APP = current_app


class FederationResponse:
    """

    This is a collection of methods to facilitate federated queries across the CanDIG network

    :param request: The type of HTTP request to federate, either GET or POST. PUT TBD
    :type request: str
    :param url: URL of the CanDIG service to be queried
    :type url: str
    :param endpoint_path: Specific API endpoint of CanDIG service to be queried, may contain query string if GET
    :type endpoint_path: str
    :param endpoint_payload: Query string or data needed by endpoint specified in endpoint_path
    :type endpoint_payload: object, {param0=value0, paramN=valueN} for GET, JSON struct dependent on service endpoint for POST
    :param request_dict: Flask request object to be modified and forwarded along to service
    :type request_dict: Flask.Request
    :param service: Name of CanDIG service to be queried, used for log tracking
    :type service: str
    :param return_mimetype: HTTP content-type, default is application/json
    :type return_mimetype: str
    :param timeout: Wait time before a request times out, default is 5 seconds
    :type timeout: int
    """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments


    def __init__(self, request, url, endpoint_path, endpoint_payload, request_dict, endpoint_service, return_mimetype='application/json',
                 timeout=5):
        """Constructor method
        """
        self.results = []
        self.status = []
        self.request = request
        self.url = url
        self.endpoint_path = endpoint_path
        self.endpoint_payload = endpoint_payload
        self.endpoint_service = endpoint_service
        self.return_mimetype = return_mimetype
        self.request_dict = request_dict
        self.logger = APP.logger
        
        try:
            self.token = self.request_dict.headers['Authorization']
        except KeyError as e:
            self.logger.warn("Request lacking Authorization header")
            self.token = ""

        self.header = {
            'Content-Type': self.return_mimetype,
            'Accept': self.return_mimetype,
            'Federation': 'false',
            'Authorization': self.token,
        }

        self.service_headers = {}
        self.timeout = timeout

    def announce_fed_out(self, request_type, destination, path):
        """
        Logging function to track requests being sent out by the Federation service

        :param request_type: The type of HTTP request to federate, either GET or POST. PUT TBD
        :type request_type: str
        :param destination: URL of service
        :type destination: str
        :param path: API endpoint of service
        :type path: Str
        """
        self.logger.info(json.dumps({"Sending": "{} -> {}/{}".format(
            request_type, destination, path
        )}))

    def announce_fed_in(self, source, code):
        """
        Logging function to track requests received by Federation from CanDIG services

        :param source: URL of service sending the response
        :type source: str
        :param code: Response code
        :type code: int
        """
        self.logger.info(json.dumps({"Received": "{} From {}".format(
            code, source
        )}))


    def get_service(self, url, endpoint_path, endpoint_payload):
        """
        Sends a GET request to service specified by url, adds response to self.status and self.results

        :param url: URL of service sending the response
        :param endpoint_path: Specific API endpoint of CanDIG service to be queried, may contain query string if GET
        :type endpoint_path: str
        :param endpoint_payload: Query parameters needed by endpoint specified in endpoint_path
        :type endpoint_payload: object, {param0=value0, paramN=valueN} for GET
        """
        try:
            request_handle = requests.Session()
            full_path = "{}/{}".format(url, endpoint_path)

            # self.announce_fed_out("GET", url, endpoint_path)

            resp = request_handle.get(full_path, headers=self.header, params=endpoint_payload, timeout=self.timeout)
            self.status.append(resp.status_code)


            if isinstance(resp.json(), list):
                self.results.extend(resp.json())
                # self.announce_fed_in(full_path, resp.status_code, resp.json())
            else:
                # Only take the 'data' portion of the Response

                response = [{key: value for key, value in resp.json().items() if key.lower()
                             not in ['headers', 'url']}]
                # self.announce_fed_in(full_path, resp.status_code, response)
                self.results.extend(response)

        except requests.exceptions.ConnectionError:
            self.status.append(404)
            return
        except requests.exceptions.Timeout:
            self.status.append(504)
            return
        except AttributeError as e:
            self.status.append(500)
            print(e)
            return

    def federate_check(self):
        """Checks if Federation conditions are met

        :return: Boolean
        """
        if 'Federation' in self.request_dict.headers and \
                self.request_dict.headers.get('Federation').lower() == 'false':
            return False
        else:
            return True

    def post_service(self, url, endpoint_path, endpoint_payload):
        """
        Sends a POST request to service specified by url, adds response to self.status and self.results

        :param url: URL of service sending the response
        :param endpoint_path: Specific API endpoint of CanDIG service to be queried, may contain query string if GET
        :type endpoint_path: str
        :param endpoint_payload: Query parameters needed by endpoint specified in endpoint_path
        :type endpoint_payload: object, JSON struct dependent on service endpoint for POST
        """
        try:
            request_handle = requests.Session()
            full_path = "{}/{}".format(url, endpoint_path)
            # self.announce_fed_out("POST", url, endpoint_path, endpoint_payload)
            resp = request_handle.post(full_path, headers=self.header, json=endpoint_payload)
            self.status.append(resp.status_code)

            if isinstance(resp.json(), list):
                self.results.extend(resp.json())
                # self.announce_fed_in(full_path, resp.status_code, resp.json())

            else:
                # Only take the 'data' portion of the Response
                response = [{key: value for key, value in resp.json().items() if key.lower()
                             not in ['headers', 'url', 'args', 'json']}]
                # self.announce_fed_in(full_path, resp.status_code, resp.json())
                self.results.extend(response)

        except requests.exceptions.ConnectionError:
            self.status.append(404)
            return

        except requests.exceptions.Timeout:
            self.status.append(504)
            return
            
        except AttributeError as e:
            self.status.append(500)
            print(e)
            return

    def handle_peer_request(self, request, endpoint_path, endpoint_payload, endpoint_service, header):
        """
        Make peer data requests and update the results and status for a FederationResponse

        If a response from a peer is received, it will be a Response Object with key pairs
            {"status": [], "results":[], "service": "name" }

        The data structures within results are still unknown/undefined at this time, so
        just append everything instead of attempting to aggregate internal structs.

        :param request: The type of HTTP request to federate, either GET or POST. PUT TBD
        :type request: str
        :param endpoint_path: Specific API endpoint of CanDIG service to be queried, may contain query string if GET
        :type endpoint_path: str
        :param endpoint_payload: Query string or data needed by endpoint specified in endpoint_path
        :type endpoint_payload: object, {param0=value0, paramN=valueN} for GET, JSON struct dependent on service endpoint for POST
        :param endpoint_service: Specific microservice name, should match a service listed in services.json config
        :type endpoint_service: str
        :param header: Request headers defined in self.headers
        :type header: object
        :return: List of ResponseObjects, this specific return is used only in testing
        """

        uri_list = []

        for peer in APP.config["peers"].values():
            uri_list.append("{}".format(peer))

        for future_response in self.async_requests(url_list=uri_list,
                                                   request=request,
                                                   header=header,
                                                   endpoint_payload=endpoint_payload,
                                                   endpoint_path=endpoint_path,
                                                   endpoint_service=endpoint_service):
            try:
                response = future_response.result()
            except AttributeError:
                if isinstance(future_response, requests.exceptions.ConnectionError):
                    self.status.append(404)
                if isinstance(future_response, requests.exceptions.Timeout):
                    self.status.append(504)

                continue
            except requests.exceptions.ConnectionError:
                self.status.append(404)
                continue

            except requests.exceptions.Timeout:
                self.status.append(504)
                continue

            # If the call was successful append the results
            if response.status_code in [200, 201, 405]:
                try:
                    """
                    Each Response will be in the form on a ResponseObject
                        {"status": [], "results": [], "service": "name"}
                    Gather the data within each "results" and append it to
                    the main one.
                    """

                    self.results.extend(response.json()["results"])
                    self.status.append(response.status_code)

                except KeyError:
                    # No "results"
                    self.logger.warn(KeyError)
                    self.status.append(500)
                    self.results.append(
                        {"Error": "Malformed Response Object: No 'results'"})
                    pass

                except ValueError:
                    # JSON decoding failure
                    self.logger.warn(ValueError)
                    self.status.append(500)
                    self.results.append(
                        {"Error": "Malformed Response Object: No JSON data"})
                    pass


        # Return is used for testing individual methods
        return self.results

    def async_requests(self, url_list, request, endpoint_path, endpoint_payload, endpoint_service, header):
        """Send requests to each CanDIG node in the network asynchronously using FutureSession. The
        futures are returned back to and handled by handle_peer_requests()


        :param url_list: List of
        :param request: The type of HTTP request to federate, either GET or POST. PUT TBD
        :type request: str
        :param endpoint_path: Specific API endpoint of CanDIG service to be queried, may contain query string if GET
        :type endpoint_path: str
        :param endpoint_payload: Query string or data needed by endpoint specified in endpoint_path
        :type endpoint_payload: object, {param0=value0, paramN=valueN} for GET, JSON struct dependent on service endpoint for POST
        :param endpoint_service: Specific microservice name, should match a service listed in services.json config
        :type endpoint_service: str
        :param header: Request headers defined in self.headers
        :type header: object
        :return: List of Futures
        """

        args = {"request_type": request, "endpoint_path": endpoint_path, "endpoint_payload": endpoint_payload, "endpoint_service": endpoint_service}
        async_session = FuturesSession(max_workers=10)  # capping max threads
        responses = []

        for url in url_list:
            try:
                # self.announce_fed_out(request_type, url, endpoint_path, endpoint_payload)
                responses.append(async_session.post(url,
                                                    json=args, headers=header, timeout=self.timeout))
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                responses.append(e)

        return responses

    def merge_status(self, statuses):
        """Returns a single status to represent the federated query.

        Priority List:
        1. Return 200 if one exists within the list
        2. 201 > 405 > 504 > 404 > 500

        :param statuses: List of integer response codes
        :type statuses: list
        :return: Single response code
        :rtype: int
        """

        if len(statuses) == 1:
            return statuses[0]

        elif 200 in statuses:
            return 200

        elif 201 in statuses:
            return 201

        elif 405 in statuses:
            return 405
    
        elif 504 in statuses:
            return 504

        elif 404 in statuses:
            return 404

        elif 500 in statuses:
            return 500

        else:
            return 500

    def get_response_object(self):
        """Driver method to communicate with other CanDIG nodes.

        1. Check if federation is needed
        1a. Broadcast if needed
        2. If no federation is required, pass endpoint to service
        3. Aggregate and return all the responses.

        :return: response_object, Status
        :rtype: object, int
        """

        if self.request == "GET":

            if self.federate_check():

                self.handle_peer_request(request="GET",
                                         endpoint_path=self.endpoint_path,
                                         endpoint_payload=self.endpoint_payload,
                                         endpoint_service=self.endpoint_service,
                                         header=self.header)

            else:
                self.get_service(url=self.url,
                                 endpoint_path=self.endpoint_path,
                                 endpoint_payload=self.endpoint_payload)
        else:

            if self.federate_check():
                self.handle_peer_request(request="POST",
                                         endpoint_path=self.endpoint_path,
                                         endpoint_payload=self.endpoint_payload,
                                         endpoint_service=self.endpoint_service,
                                         header=self.header)
            else:
                self.post_service(url=self.url,
                                  endpoint_path=self.endpoint_path,
                                  endpoint_payload=self.endpoint_payload)

        status = self.merge_status(self.status)
        try:
            # Remove duplicates from a list response due to Federated querying
            response = {"status": status, "results": sorted(list(set(self.results))), "service": self.endpoint_service}

        except TypeError:
            # Dealing with dicts objects
            response = {"status": status, "results": self.results, "service": self.endpoint_service}
        
        return response, status


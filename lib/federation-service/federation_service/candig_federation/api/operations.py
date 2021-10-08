"""
Methods to handle incoming requests passed from Tyk
"""


import json
import flask
import sys
from candig_federation.api.logging import apilog
from candig_federation.api.federation import FederationResponse

APP = flask.current_app

  
@apilog
def post_search():
    """
    Send a POST request to CanDIG services and possibly federate it.
    Method defined by federation.yaml OpenAPI document.
    Retrieves an endpoint_path and endpoint_payload from POST request body,
    following the endpoint_path conventions set in get_search().
    The endpoint_payload is microservice specific but will typically be a
    JSON object of sorts.
    
    :return: response_object
    response_object: json string
    Merged responses from the federation nodes. response_object structure:
    ** This still needs to be finalized **
    {
    "status": Status,
    "results": [Response],
    "service": ServiceName
    }

    Status - Aggregate HTTP response code
    Response - List of service specific responses
    ServiceName - Name of service (used for logstash tagging)
    """
    try:

        data = json.loads(flask.request.data)
        request_type = data["request_type"]
        endpoint_path = data["endpoint_path"]
        if endpoint_path[0] == "/":
            return {
                    "response": ("Invalid endpoint_path: {}. "
                    "Please remove the / at the beginning: ".format(endpoint_path)),
                    "status": 400,
                    "service": "ErrorHandling"
                    }, 400

        endpoint_payload = data["endpoint_payload"]
        endpoint_service = data["endpoint_service"]
        microservice_URL = APP.config['services'][endpoint_service]
        federation_response = FederationResponse(url=microservice_URL,
                                                request=request_type,
                                                endpoint_path=endpoint_path,
                                                endpoint_payload=endpoint_payload,
                                                request_dict=flask.request,
                                                endpoint_service=endpoint_service
                                                )
        return federation_response.get_response_object()

    except KeyError:
        """     
        Due to Connexion parsing the args prior this code running, it will be assumed that we
        have a valid request_type, endpoint_path and endpoint_payload. A KeyError occuring here 
        will be due to the service dictionary receiving an invalid key.
        """
    return {
           "response": ("Invalid service name: {}. "
           "Please make sure that the service requested matches a registered service: "
           "{} "
           .format(endpoint_service, list(APP.config['services'].keys()))),
           "status": 404,
           "service": "ErrorHandling"
           }, 404


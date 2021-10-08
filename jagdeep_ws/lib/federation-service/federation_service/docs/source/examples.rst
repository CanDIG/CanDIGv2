Sending a Request
=================

There are a number of ways to send requests to the Federation service, ranging from 
simple cURL commands, to programs such as Insomnia or Postman. Regardless of method, the POST
request being sent out needs to have four parameters:

| **request_type**: This needs to be either GET or POST, and will tell the federation service what type of request to forward on to the microservice.

| **endpoint_service**: This should be a name matching a key in the services.json configuration file.

| **endpoint_path**: The microservice endpoint being queried without any initial backslash, as the Federation service will add one in when constructing the full path to the microservice.

| **endpoint_payload**: Any additional arguments needed to be past on to microservice endpoints. Should be an empty object ({}) if nothing is required.




Why No GET?
===========

A question that may come to mind when looking at these examples is why specify GET or POST within a POST request_handle
rather than just sending a GET request directly to be passed on? This was the case at first, but it quickly became convoluted
to pass complex search queries as strings formatted as dictionaries or json objects. Utilizing the POST body to pass on all the
endpoint arguments to a GET request makes it much easier from both a user and coding standpoint.


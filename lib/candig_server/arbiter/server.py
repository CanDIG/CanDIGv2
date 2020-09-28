# CanDIG-Server Arbiter
#from flask import Flask, request
import random
import json
import requests

#from quart import jsonify, Quart, request
import os
import time
import threading


#app = Quart(__name__)
#app = Flask(__name__)


# --- environment vars
try:
    mode = os.environ["ARBITER_MODE"] # debug | prod  
except Exception as e:
    #print(e) 
    mode="prod"
    print(f"Default Running Mode : {mode}")
    #raise e

try:
    port = os.environ["ARBITER_INTERNAL_PORT"]        
except Exception as e:
    port="3002"
    print(f"Default Port : {port}")

try:
    resource_authz_host = os.environ["RESOURCE_AUTHZ_HOST"]    
except Exception as e:
    resource_authz_host="0.0.0.0"
    print(f"Default Resource Authz Host : {resource_authz_host}")

try:
    resource_authz_port = os.environ["RESOURCE_AUTHZ_PORT"]    
except Exception as e:
    resource_authz_port="8181"
    print(f"Default Resource Authz Port : {resource_authz_port}")

try:
    resource_host = os.environ["RESOURCE_HOST"]    
except Exception as e:
    resource_host="0.0.0.0"
    print(f"Default Resource Host : {resource_host}")

try:
    resource_port = os.environ["RESOURCE_PORT"]    
except Exception as e:
    resource_port="3001"
    print(f"Default Resource Port : {resource_port}")




authz_url=f"http://{resource_authz_host}:{resource_authz_port}/v1/data/permissions/allowed"

# ---

# # Route all paths and methods
# # @app.route("/", defaults={"path": ""})
# # @app.route("/<path:path>")
# @app.route('/', defaults={'u_path': ''})
# @app.route('/<path:u_path>')
# def route_all(u_path):
   

#     # except Exception as e:
#     #     print(e)
#     #     return 'error'


# if __name__ == '__main__':
#     app.run(debug=(mode == "debug"), host='0.0.0.0', port=port)



import asyncio

from aiohttp import web

@asyncio.coroutine
async def handle(request):
    #try:
    # prepare data
    #train_request_json = await request.get_json()

    try:
        authN_token_header = request.headers['Authorization']
        authZ_token_header = request.headers['X-CanDIG-Authz']
    except Exception as e:
        print(e)
        return 'authorization error'

    authN_token = authN_token_header
    authZ_token = authZ_token_header


    # split from 'Bearer '
    if "Bearer " in authN_token:
        authN_token = authN_token.split()[1]

    if "Bearer " in authZ_token:
        authZ_token = authZ_token.split()[1]


    print(f"Path: {request.path}")
    # print(f"Found token: {authN_token}")
    # print(f"Found token: {authZ_token}")


    # reach resource authz server
    opa_request = { 
        "input" : {
            "kcToken" : authN_token,
            "vaultToken": authZ_token
        }
    }

    try:
        response = requests.post(authz_url, json=opa_request)
        # check response
        allow = response.json()
        if 'code' in allow and allow['code'] == 'internal_error':
            return web.HTTPInternalServerError(body=json.dumps({'error': json.dumps(allow)}))
        
    except Exception as e:
        print(e)
        return web.HTTPInternalServerError(body=json.dumps({'error': f'Unknown error: {e}'}))


    if 'result' in allow and allow['result'] == True:
        # forward request to resource server
        try:
            url=f"http://{resource_host}:{resource_port}{request.path}"

            print(f"Calling URL : {url} using method {request.method}")

            if request.method == "GET" :
                # simply get resource
                resource = requests.get(url)
            else:
                # assume json payload from inbound request
                payload = await request.text()

                # relay body to resource
                resource = requests.post(url, data=payload)

            print(f'returning {resource}')

            # naively return all headers and all content
            return web.Response(headers=resource.headers, body=resource.content)

        except Exception as e:
            print(e)
        
    return web.HTTPUnauthorized(body=json.dumps({'error': 'Access Denied'}))

    
    
    # print('there was a request')
    # text = "Hello "
    # return web.Response(body=text.encode('utf-8'))

@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)

    # accept all GET and POST calls with any path
    app.router.add_route('GET', '/{tail:.*}', handle)
    app.router.add_route('POST', '/{tail:.*}', handle)

    # start server
    srv = yield from loop.create_server(app.make_handler(), '0.0.0.0', port)
    print(f"Server started at http://0.0.0.0:{port}")
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass 
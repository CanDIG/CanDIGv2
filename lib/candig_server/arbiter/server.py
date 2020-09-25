# CanDIG-Server Arbiter
from flask import Flask, request
import random
import json
import math
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import numpy as np
import requests

#from quart import jsonify, Quart, request

import time
import threading

authz_url="http://0.0.0.0:8181/v1/data/permissions/allowed"

#app = Quart(__name__)
app = Flask(__name__)

# Route all paths and methods
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def route_all(path):
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


        print(f"Found token: {authN_token}")
        print(f"Found token: {authZ_token}")

        #print(train_request_json)

        # id = train_request_json["AnalysisId"]
        # X = np.array(train_request_json["X"])
        # y = np.array(train_request_json["y"])
        # wh = train_request_json["WebHook"]

        # run training async task
        # t1 = threading.Thread(target=handle_multi_reg_training, args=(id, X, y, wh))
        # t1.start()

        opa_request = { 
            "input" : {
                "kcToken" : authN_token,
                "vaultToken": authZ_token
            }
        }


        # forward request to resource server
        try:
            response = requests.post(authz_url, json=opa_request)
            # check response
            allow = response.json()
            if 'code' in allow and allow['code'] == 'internal_error':
                return 'authz error'

            
        except Exception as e:
            print(e)
            return 'error'


        #print(f"path: {path}, allow: {allow['result']}")
        print(f"path: {path}, response: {allow}")
        
        if 'result' in allow and allow['result'] == True:
            # forward request to resource server
            try:
                resource = requests.request(request.method, f"http://0.0.0.0:3001/{path}")
                print(f'returning {resource}')
                return resource.content
            except Exception as e:
                print(e)
                return 'error'
            

        print(f'returning {allow}')
        return allow

    # except Exception as e:
    #     print(e)
    #     return 'error'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='3002')
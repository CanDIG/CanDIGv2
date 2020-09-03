// Virtual token endpoint for API Gateway

tokenHelper = {
    handleTykRequest: function(requestObj) {
        var encodedResponse = TykMakeHttpRequest(JSON.stringify(requestObj));
        var decodedResponse = JSON.parse(encodedResponse);
        try {
            var decodedBody = JSON.parse(decodedResponse.Body);
        } catch (err) {
            decodedBody = {}
        }
        return decodedBody
    },

    getOIDCToken: function(body, spec) {
        tokenRequest = {
            "Method": "POST",
            "FormData": body,
            "Headers": {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            "Domain": spec.config_data.KC_SERVER,
            "Resource": "/auth/realms/" + spec.config_data.KC_REALM + "/protocol/openid-connect/token"
        }
        return tokenHelper.handleTykRequest(tokenRequest)
    }
}

function tokenHandler(request, session, spec) {
    try {
        var requestBody = JSON.parse(request.Body)
        var username = requestBody["username"]
        var password = requestBody["password"]

        body = {
            "username": username,
            "password": password,
            "grant_type": "password",
            "scope": "openid",
            "client_id": spec.config_data.KC_CLIENT_ID,
            "client_secret": spec.config_data.KC_SECRET
        }

        var decodedBody = tokenHelper.getOIDCToken(body, spec)
        var idToken = decodedBody["id_token"]

        if (idToken) {
            var responseObject = {
                Body: JSON.stringify({"id_token": idToken}),
                Headers: {
                    "Content-Type": "application/json"
                },
                Code: 200
            }

        } else {
            var responseObject = {
                Body: JSON.stringify({"error": "Invalid credentials"}),
                Headers: {
                    "Content-Type": "application/json"
                },
                Code: 401
            }
        }

    } catch(err) {
        responseObject = {
            Body: JSON.stringify({"error": "Invalid request object"}),
            Headers: {
                "Content-Type": "application/json"
            },
            Code: 401
        }
    }

    return TykJsResponse(responseObject, session.meta_data)
}

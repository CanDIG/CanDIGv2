// Virtual authentication login endpoint for API Gateway

var loginHelper = {
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

    loginRedirect: function(spec, app) {
        var url = spec.config_data.KC_SERVER
        url += '/auth/realms/' + spec.config_data.KC_REALM
        url += '/protocol/openid-connect/auth?scope=' + spec.config_data.KC_SCOPE
        url += '&response_type=' + spec.config_data.KC_RTYPE
        url += '&client_id=' + spec.config_data.KC_CLIENT_ID
        url += '&response_mode=' + spec.config_data.KC_RMODE
        url += '&redirect_uri=' + spec.config_data.TYK_SERVER + '/auth/login'

        redirectBody = {
            Body: "{}",
            Headers: {
                "Location": url,
            },
            Code: 302
        }

        if (app) {
            redirectBody.Headers["Set-Cookie"] = "tyk_app=" + app[0] + ";Path=/;HttpOnly";
        }

        return redirectBody
    },

    getCookie: function(request, name) {
        var splitCookie = request.Headers["Cookie"][0].split("; ");
        var valueCookie = _.find(splitCookie, function(cookie) {
            if (cookie.indexOf(name+"=") > -1) {
                return cookie
            }
        });
        return valueCookie
    },

    setCookie: function(token, spec) {
        var cookie = "session_id=" + token
        cookie += ";Path=/" 
        cookie += ";Max-Age=" + spec.config_data.MAX_TOKEN_AGE
        cookie += ";HttpOnly"

        if (spec.config_data.USE_SSL) {
            cookie += ";Secure"
        }
        return cookie
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
        return loginHelper.handleTykRequest(tokenRequest)
    }
}


function loginHandler(request, session, spec) {
    log("Virtual Login Handler")
    var code = request.Params["code"]

    if (code === undefined) {
        var app = request.Params["app_url"]
        var responseObject = loginHelper.loginRedirect(spec, app)
    } else {
        body = {
            "client_id": spec.config_data.KC_CLIENT_ID,
            "client_secret": spec.config_data.KC_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": spec.config_data.TYK_SERVER + '/auth/login',
            "code": code[0]
        }

        var decodedBody = loginHelper.getOIDCToken(body, spec)
        var location = loginHelper.getCookie(request, "tyk_app")

        if (location) {
            location = location.split("=")[1];
        } else {
            location = ""
        }

        if (_.has(decodedBody, "id_token")) {
            var idToken = decodedBody["id_token"]
            var responseObject = {
                Body: "Success",
                Headers: {
                    "Authorization": "Bearer " + idToken,
                    "Set-Cookie": loginHelper.setCookie(idToken, spec),
                    "Location": spec.config_data.TYK_SERVER + location
                },
                Code: 302
            }

        } else {
            if (_.has(decodedBody, "error")) {
                log(decodedBody["error"] + ":" + decodedBody["error_description"])
            } 
            var responseObject = {
                Body: JSON.stringify(decodedBody),
                Headers: {
                    "Content-Type": "application/json"
                },
                Code: 403
            }
        }
    }

    return TykJsResponse(responseObject, session.meta_data)
}
log("Virtual authentication endpoint initialised")
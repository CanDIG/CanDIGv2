// ---- Frontend Authentication middleware -----

var frontendAuthMiddleware = new TykJS.TykMiddleware.NewMiddleware({});

function getCookie(request, cookie_name) {
    if (!("Cookie" in request.Headers)) {
	return undefined;
    }
    var splitCookie = request.Headers["Cookie"][0].split("; ");
    var valueCookie = _.find(splitCookie, function(cookie) {
        if (cookie.indexOf(cookie_name+"=") > -1) {
            return cookie
        }
    });

    return valueCookie
}

function exchangeRefreshTokenForIdToken(refreshToken, request, spec) {
    body = {
        "grant_type": "refresh_token",
        "client_id": spec.config_data.KEYCLOAK_CLIENT_ID,
        "client_secret": spec.config_data.KEYCLOAK_SECRET,
        "refresh_token": refreshToken
    }
    
    tokenRequest = {
        "Method": "POST",
        "FormData": body,
        "Headers": {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        "Domain": spec.config_data.KEYCLOAK_PRIVATE_URL,
        "Resource": "/auth/realms/" + spec.config_data.KEYCLOAK_REALM + "/protocol/openid-connect/token"
    }
    
    var encodedResponse = TykMakeHttpRequest(JSON.stringify(tokenRequest));
    var decodedResponse = JSON.parse(encodedResponse);
    try {
        var decodedBody = JSON.parse(decodedResponse.Body);
        if (decodedBody != undefined) {
            if (_.has(decodedBody, "error")) {
                log(decodedBody.error)
                return undefined
            }
            log("old token is " + refreshToken + ", refresh token is " + decodedBody.access_token)
            log(decodedBody.access_token)
            request.SetHeaders["Authorization"] = "Bearer " + decodedBody.access_token;
            return decodedBody.access_token;
        }
    } catch (err) {
        log(err)
        return undefined
    }
    return undefined
}

frontendAuthMiddleware.NewProcessRequest(function(request, session, spec) {
    log("Running Frontend Authorization JSVM middleware ")

    if (request.Headers["Authorization"] === undefined) {
        try {
            var tokenCookie = getCookie(request, "session_id")
        } catch(err) {
            log(err)
            var tokenCookie = undefined
        }
        if (tokenCookie != undefined) {
            var refreshToken = tokenCookie.split("=")[1];
            result = exchangeRefreshTokenForIdToken(refreshToken, request, spec);
            if (result != undefined) {
                request.ReturnOverrides.ResponseHeaders = {
                    "Set-Cookie": result
                }
                return frontendAuthMiddleware.ReturnData(request, session.meta_data);
            }
        }
    }
    // if we couldn't get a valid token from the cookie, send the user back to login:
    request.ReturnOverrides.ResponseCode = 302
    request.ReturnOverrides.ResponseHeaders = {
        "Location": spec.config_data.TYK_SERVER + "/auth/login?app_url=" + request.URL
    }
    return frontendAuthMiddleware.ReturnData(request, session.meta_data);
});
    
log("Authorization middleware initialised");

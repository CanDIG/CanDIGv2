// ---- Frontend Authentication middleware -----

var frontendAuthMiddleware = new TykJS.TykMiddleware.NewMiddleware({});

function getCookie(request, cookie_name) {
    if (!("Cookie" in request.Headers)) {
        return undefined;
    }
    var splitCookie = request.Headers["Cookie"][0].split("; ");
    var valueCookie = _.find(splitCookie, function (cookie) {
        if (cookie.indexOf(cookie_name + "=") > -1) {
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
        "Resource": spec.config_data.KEYCLOAK_AUTH_PREFIX + "/realms/" + spec.config_data.KEYCLOAK_REALM + "/protocol/openid-connect/token"
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
            request.SetHeaders["Authorization"] = "Bearer " + decodedBody.access_token;
            return decodedBody.refresh_token + "|" + decodedBody.access_token;
        }
    } catch (err) {
        log(err)
        return undefined
    }
    return undefined
}

function setCookie(token, spec) {
    var cookie = "session_id=" + token
    cookie += ";Path=/"
    cookie += ";Max-Age=" + spec.config_data.MAX_TOKEN_AGE
    cookie += ";HttpOnly"

    if (spec.config_data.USE_SSL) {
        cookie += ";Secure"
    }
    return cookie
};

function setupRedirect(request, spec) {
    request.ReturnOverrides.ResponseCode = 302
    request.ReturnOverrides.ResponseHeaders = {
        "Location": spec.config_data.TYK_SERVER + "/auth/login?app_url=" + request.URL
    }
    return request;
}

frontendAuthMiddleware.NewProcessRequest(function (request, session, spec) {
    log("Running Frontend Authorization JSVM middleware ");

    if (request.Headers["Authorization"] === undefined) {
        try {
            var tokenCookie = getCookie(request, "session_id")
        } catch (err) {
            log(err);
            var tokenCookie = undefined;
        }
        if (tokenCookie != undefined) {
            var tokens = tokenCookie.split("=")[1].split("|");
            var refreshToken = tokens[0];
            var accessToken = tokens[1];

            // Verify the access token before proceeding
            try {
                var tokenParts = accessToken.split('.');
                if (tokenParts.length !== 3) {
                    log("Invalid JWT format");
                    setupRedirect(request, spec);
                    return frontendAuthMiddleware.ReturnData(request, session.meta_data);
                }
                // Check that all parts of the jwt are readable
                var header = JSON.parse(b64dec(tokenParts[0]));
                var payload = JSON.parse(b64dec(tokenParts[1]));
                var now = Math.floor(Date.now() / 1000);

                if (payload.exp && payload.exp < now) {
                    log("Token expired");
                    setupRedirect(request, spec);
                    return frontendAuthMiddleware.ReturnData(request, session.meta_data);
                }

                // If we get here, token format is valid and not expired
                request.SetHeaders["Authorization"] = "Bearer " + accessToken;
                return frontendAuthMiddleware.ReturnData(request, session.meta_data);
            } catch (err) {
                log(err);

                // If we've encountered an error with the access token, attempt to use the refresh token, and then
                // force them to refresh the page
                result = exchangeRefreshTokenForIdToken(refreshToken, request, spec);
                if (result != undefined) {
                    request.ReturnOverrides = {
                        "ResponseCode": 302,
                        "ResponseBody": "",
                        "ResponseHeaders": {
                            "Set-Cookie": setCookie(result, spec),
                            "Refresh": "0;url=/"
                        }
                    };
                    return frontendAuthMiddleware.ReturnData(request, session.meta_data);
                }
            }
        }
    }
    // if we couldn't get a valid token from the cookie, send the user back to login:
    setupRedirect(request, spec);
    return frontendAuthMiddleware.ReturnData(request, session.meta_data);
});

log("Authorization middleware initialised");

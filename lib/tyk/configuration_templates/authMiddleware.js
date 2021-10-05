// ---- Authentication middleware -----

var authMiddleware = new TykJS.TykMiddleware.NewMiddleware({});

var iss = "${TEMP_KEYCLOAK_PUBLIC_URL}/auth/realms/${KEYCLOAK_REALM}"
var aud = "${KEYCLOAK_CLIENT_ID}"

var full_authn_pk="-----BEGIN PUBLIC KEY-----\n${KEYCLOAK_PUBLIC_KEY}\n-----END PUBLIC KEY-----"



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

function isTokenExpired(decodedPayload) {
    log("-- Checking token expiration --")
    tokenExpires = decodedPayload["exp"]
    sysTime = (new Date).getTime()/1000 | 0;

    return sysTime>tokenExpires
}

authMiddleware.NewProcessRequest(function(request, session, spec) {
    log("Running Authorization JSVM middleware")

    log("Checking Authorization")
    if (request.Headers["Authorization"] === undefined) {
        try {
            log("Checking Cookie")
            var tokenCookie = getCookie(request, "session_id")
        } catch(err) {
            log(err)
            var tokenCookie = undefined
        }

        if (tokenCookie != undefined) {
            log("Manipulating Cookie")
            var idToken = tokenCookie.split("=")[1];

            tokenPayload = idToken.split(".")[1]
            payloadPadding = tokenPayload.length % 4
            
            if (payloadPadding != 0) {
                _.times(4-payloadPadding, function() {
                    tokenPayload += "="
                })
            }

            decodedPayload = JSON.parse(b64dec(tokenPayload))
        
            if (isTokenExpired(decodedPayload)) {
                request.ReturnOverrides.ResponseCode = 302;
                request.ReturnOverrides.ResponseHeaders = {
                    "Location": spec.config_data.TYK_SERVER + "/auth/login?app_url=" + request.URL
                };
                log(request.URL);

            } else{
                request.SetHeaders["Authorization"] = "Bearer " + idToken;
            }

        } else {
            if (spec.config_data.SESSION_ENDPOINTS === undefined) {
                request.ReturnOverrides.ResponseCode = 302
                request.ReturnOverrides.ResponseHeaders = {
                    "Location": spec.config_data.TYK_SERVER + "/auth/login?app_url=" + request.URL
                }
            } else if (_.contains(spec.config_data.SESSION_ENDPOINTS, request.URL)) {
                request.ReturnOverrides.ResponseCode = 302
                request.ReturnOverrides.ResponseHeaders = {
                    "Location": spec.config_data.TYK_SERVER + "/auth/login?app_url=" + request.URL
                }
            } else {
                request.ReturnOverrides.ResponseCode = 403
                request.ReturnOverrides.ResponseError = "Valid access token required"
            } 
        }
    }
    
    return authMiddleware.ReturnData(request, session.meta_data);
});
    
log("Authorization middleware initialised");

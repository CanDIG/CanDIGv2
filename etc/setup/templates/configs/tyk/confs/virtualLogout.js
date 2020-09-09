// Virtual authentication logout endpoint for API Gateway

logoutHelper = {
    setCookie: function(app) {
        var cookie = "session_id=;"
        cookie += "Path=/;" 
        cookie += "Max-Age=0;"
        cookie += "HttpOnly;"

        if (app) {
            cookie += "tyk_app=" + app[0] + ";Path=/;"
        }
        return cookie
    },

    logoutUrl: function(spec) {
        var url = spec.config_data.KC_SERVER
        url += '/auth/realms/' + spec.config_data.KC_REALM
        url += '/protocol/openid-connect/logout?redirect_uri=' + spec.config_data.TYK_SERVER + '/auth/login'
        return url
    }
}

function logoutHandler(request, session, spec) {
    log("Logging out")
    var app = request.Params["app_url"]
    
    responseObject = {
        Body: "{}",
        Headers: {
            "Location": logoutHelper.logoutUrl(spec),
            "Set-Cookie": logoutHelper.setCookie(app)
        },
        Code: 302
    }

    return TykJsResponse(responseObject, session.meta_data)
}
log("Virtual logout endpoint initialised")
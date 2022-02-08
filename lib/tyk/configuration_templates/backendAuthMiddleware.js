// ---- Backend Authentication middleware -----

var backendAuthMiddleware = new TykJS.TykMiddleware.NewMiddleware({});

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

backendAuthMiddleware.NewProcessRequest(function(request, session, spec) {
    // log("Running Authorization JSVM middleware")

    if (request.Headers["Authorization"] === undefined) {
        try {
            var tokenCookie = getCookie(request, "session_id")
            var idToken = tokenCookie.split("=")[1];
            request.SetHeaders["Authorization"] = "Bearer " + idToken;
        } catch(err) {
            log(err)
            var tokenCookie = undefined
        }
    }
    
    return backendAuthMiddleware.ReturnData(request, session.meta_data);
});
    
log("Authorization middleware initialised");

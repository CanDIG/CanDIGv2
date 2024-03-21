// Virtual authentication logout endpoint for API Gateway

logoutHelper = {
  setCookie: function (app) {
    var cookie = "session_id=;";
    cookie += "Path=/;";
    cookie += "Max-Age=0;";
    cookie += "HttpOnly;";

    if (app) {
      cookie += "tyk_app=" + app[0] + ";Path=/;";
    }
    return cookie;
  },
  getCookie: function (request, name) {
    var splitCookie = request.Headers["Cookie"][0].split("; ");
    var valueCookie = _.find(splitCookie, function (cookie) {
      if (cookie.indexOf(name + "=") > -1) {
        return cookie;
      }
    });
    return valueCookie;
  },

  logoutUrl: function (spec, idToken) {
    var url = spec.config_data.KEYCLOAK_SERVER;
    url += "/auth/realms/" + spec.config_data.KEYCLOAK_REALM;
    url +=
      "/protocol/openid-connect/logout?post_logout_redirect_uri=" +
      spec.config_data.TYK_SERVER +
      "/auth/login";
    url += "&id_token_hint=" + idToken;
    return url;
  },

  getSessionID: function (request, spec) {
    var sessionToken = logoutHelper.getCookie(request, "session_id");
    refreshToken = sessionToken.split("=")[1];
    body = {
      grant_type: "refresh_token",
      client_id: spec.config_data.KEYCLOAK_CLIENT_ID,
      client_secret: spec.config_data.KEYCLOAK_SECRET,
      refresh_token: refreshToken,
    };

    tokenRequest = {
      Method: "POST",
      FormData: body,
      Headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      Domain: spec.config_data.KEYCLOAK_PRIVATE_URL,
      Resource:
        "/auth/realms/" +
        spec.config_data.KEYCLOAK_REALM +
        "/protocol/openid-connect/token",
    };

    var encodedResponse = TykMakeHttpRequest(JSON.stringify(tokenRequest));
    var decodedResponse = JSON.parse(encodedResponse);
    try {
      var decodedBody = JSON.parse(decodedResponse.Body);
    } catch (err) {
      decodedBody = {};
    }
    return decodedBody;
  },
};

function logoutHandler(request, session, spec) {
  log("Logging out");
  var app = request.Params["app_url"];

  var decodedBody = logoutHelper.getSessionID(request, spec);

  if (_.has(decodedBody, "id_token")) {
    responseObject = {
      Body: "{}",
      Headers: {
        Location: logoutHelper.logoutUrl(spec, decodedBody.id_token),
        "Set-Cookie": logoutHelper.setCookie(app),
      },
      Code: 302,
    };
  }

  return TykJsResponse(responseObject, session.meta_data);
}
log("Virtual logout endpoint initialised")
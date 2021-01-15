{
    "api_id": "${TYK_AUTH_API_ID}",
    "use_keyless": true,
    "active": true,
    "strip_auth_data": false,
    
    "config_data": {
      "KC_RTYPE": "code",
      "KC_REALM": "${KC_REALM}",
      "KC_CLIENT_ID": "${KC_CLIENT_ID}",
      "KC_SERVER": "${KEYCLOAK_SERVICE_PUBLIC_URL}",
      "KC_SCOPE": "openid+email",
      "KC_RMODE": "query",
      "USE_SSL": false,
      "KC_SECRET": "${KC_SECRET}",
      "TYK_SERVER": "${CANDIG_PUBLIC_URL}",
      "MAX_TOKEN_AGE": 43200
    },

    "auth": {
	"auth_header_name": ""
    },

    "name": "${TYK_AUTH_API_NAME}",
    "slug": "${TYK_AUTH_API_SLUG}",

    "proxy": {
	"target_url": "${TYK_LOGIN_TARGET_URL}/auth/login",
	"strip_listen_path": false,
	"listen_path": "/auth/"
    },

    "version_data": {
	"not_versioned": true,
	"versions": {
	    "Default": {
		"name": "Default",
		"use_extended_paths": true,
		"extended_paths": {
		    "virtual": [
                        {
			    "response_function_name": "logoutHandler",
			    "function_source_type": "file",
			    "function_source_uri": "middleware/virtualLogout.js",
			    "path": "logout",
			    "method": "GET",
			    "use_session": false,
			    "proxy_on_error": false
		        },
			{
			    "response_function_name": "tokenHandler",
			    "function_source_type": "file",
			    "function_source_uri": "middleware/virtualToken.js",
			    "path": "token",
			    "method": "POST",
			    "use_session": false,
			    "proxy_on_error": false
			},
			{
			    "response_function_name": "loginHandler",
			    "function_source_type": "file",
			    "function_source_uri": "middleware/virtualLogin.js",
			    "path": "login",
			    "method": "GET",
			    "use_session": false,
			    "proxy_on_error": false
			}
		    ],
		    "do_not_track_endpoints": [{
			"path": "token",
			"method": "POST"
		    }]
		}
	    }
	}
    }
}

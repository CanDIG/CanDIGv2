{
    "api_id": "${TYK_CANDIG_API_ID}",
    "name": "${TYK_CANDIG_API_NAME}",
    "use_openid": true,
    "active": true,
    "slug": "${TYK_CANDIG_API_SLUG}",

    "enable_signature_checking": false,

    "jwt_issued_at_validation_skew": 0,
    "jwt_expires_at_validation_skew": 0,
    "upstream_certificates": {},
    "use_keyless": false,
    "enable_coprocess_auth": false,
    "base_identity_provided_by": "",
    
    "proxy": {
	"target_url": "${TYK_TARGET_URL}",
	"strip_listen_path": true,
        "disable_strip_slash": false,
	"listen_path": "/${TYK_LISTEN_PATH}",
        "transport": {
            "ssl_insecure_skip_verify": false,
            "ssl_ciphers": [],
            "ssl_min_version": 0,
            "proxy_url": ""
        },
        "target_list": [],
        "preserve_host_header": false
    },

    "version_data": {
	"not_versioned": true,
	"versions": {
	    "Default": {
		"name": "Default",
		"use_extended_paths": true
	    }
	},
        "extended_paths": {
            "ignored": [
                {
                    "path": "${KEYCLOAK_LOGIN_REDIRECT_PATH}",
                    "method_actions": {
                        "GET": {
                            "action": "no_action",
                            "code": 200,
                            "headers": {}
                        }
                    }
                }
            ]
        }
    },
    "custom_middleware": {
	"pre": [
            {
	        "name": "authMiddleware",
	        "path": "/opt/tyk-gateway/middleware/authMiddleware.js",
	        "require_session": false
	    }
        ],
	"post": [
        {
	        "name": "permissionsStoreMiddleware",
	        "path": "/opt/tyk-gateway/middleware/permissionsStoreMiddleware.js",
	        "require_session": false
	    }
    ],
	"id_extractor": {
	    "extract_with": "",
	    "extract_from": "",
	    "extractor_config": {}
	},
	"driver": "",
	"auth_check": {
	    "path": "",
	    "require_session": false,
	    "name": ""
	},
	"post_key_auth": [],
	"response": []
    },
    
    "config_data": {
        "SESSION_ENDPOINTS": [
            "/",
            "/gene_search",
            "/patients_overview",
            "/sample_analysis",
            "/custom_visualization",
            "/api_info",
            "/serverinfo"
        ],
        "TYK_SERVER": "${CANDIG_PUBLIC_URL}",
        "VAULT_SERVICE_URL":"${VAULT_SERVICE_URL}",
        "VAULT_SERVICE_RESOURCE":"/v1/auth/jwt/login",
        "VAULT_ROLE":"researcher"
    },
    "openid_options": {
	"segregate_by_client": false,
	"providers": [
            {
                "issuer": "${TEMP_KEYCLOAK_SERVICE_PUBLIC_URL}/auth/realms/${KEYCLOAK_REALM}",
                "client_ids": {
                    "${KEYCLOAK_CLIENT_ID_64}": "${TYK_POLICY_ID}"
                }
            }
        ]
    },


    "definition": {
	"location": "header",
	"key": "x-api-version"
    },


    "internal": false,
    "jwt_skip_kid": false,
    "enable_batch_request_support": false,
    "response_processors": [],
    "use_mutual_tls_auth": false,
    "basic_auth": {
        "disable_caching": false,
        "cache_ttl": 0,
        "extract_from_body": false,
        "body_user_regexp": "",
        "body_password_regexp": ""
    },
    "use_standard_auth": false,
    "session_lifetime": 0,
    "use_oauth2": false,
    "jwt_source": "",
    "jwt_signing_method": "",
    "jwt_not_before_validation_skew": 0,
    "jwt_identity_base_field": "",

    "session_provider": {
        "name": "",
        "storage_engine": "",
        "meta": {}
    },

    "auth": {
        "use_param": false,
        "param_name": "",
        "use_cookie": false,
        "cookie_name": "",
        "auth_header_name": "",
        "use_certificate": false,
        "validate_signature": false,
        "signature": {
            "algorithm": "",
            "header": "",
            "secret": "",
            "allowed_clock_skew": 0,
            "error_code": 0,
            "error_message": ""
        }
    }
}

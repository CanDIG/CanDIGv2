// ---- Permissions Store middleware -----

var permissionsStoreMiddlewareUtil = {    
    
    call_vault: function (request, session, spec, authNToken) {
        log("--- Calling Vault ---")
        var vaultData = undefined;

        //TODO : boolean variable to toggle dev logging
        //log(authNToken)

        if (request.Headers["X-CanDIG-Authz"] === undefined) {

            var authorization_header = 'Bearer ' + authNToken;
            if (authorization_header == undefined) 
                throw new Error("Missing Authorization Header!");
            
            var splits = authorization_header.split(" ");
            //log(splits[0])
            if (splits[0] != "Bearer")
                throw new Error("Missing Bearer token!");

            var token = splits[1];
            var tokenPayload = token.split(".")[1];
            var decodedPayload = JSON.parse(b64dec(tokenPayload));
            //log("Decoded Payload: "+JSON.stringify(decodedPayload))
            
            
            var data = {
                "jwt": token,
                "role": spec.config_data.VAULT_ROLE
            };
            var requestParams = {
                "Method": "POST",
                "Domain": spec.config_data.VAULT_SERVICE_URL,
                "Resource": spec.config_data.VAULT_SERVICE_RESOURCE,
                "Body": JSON.stringify(data)
            };

            var resp = TykMakeHttpRequest(JSON.stringify(requestParams));
            var respJson = JSON.parse(resp);
            //log("Vault Response: " + JSON.stringify(respJson))
            
            if (respJson.Code == 200) {
                // Yup we need two JSON.parse
                var vaultJson = JSON.parse(respJson.Body);
                var vaultToken = vaultJson.auth.client_token;
                
                var headers = {
                    "X-Vault-Token": vaultToken
                };
                
                // We have validated the JWT and gotten an access token for Vault
                // we can now fetch the entitlements at /v1/secret/data/$userId
                // TODO: will have to decide on the path for these, inside vault
                // this path being user-created, we can do whatever
                var requestParams = {
                    "Headers": headers,
                    "Method": "GET",
                    "Domain": spec.config_data.VAULT_SERVICE_URL,
                    "Resource": "/v1/identity/oidc/token/" + spec.config_data.VAULT_ROLE,
                };

                var resp = TykMakeHttpRequest(JSON.stringify(requestParams));
                var respJson = JSON.parse(resp);
                //log("Vault Response: " + JSON.stringify(respJson))

                if (respJson.Code == 200) {
                    vaultData = JSON.parse(respJson.Body);

                    return vaultData;
                }
            }    
        }
    }
};



var permissionsStoreMiddleware = new TykJS.TykMiddleware.NewMiddleware({});

permissionsStoreMiddleware.NewProcessRequest(function(request, session, spec) {

    log("Running Permissions Store JSVM middleware");

    if (request.Headers["Authorization"] != undefined) {

        var authNToken = request.Headers["Authorization"][0].split(" ")[1];

        var vault_data = permissionsStoreMiddlewareUtil.call_vault(request, session, spec, authNToken);
        if(vault_data != undefined) {
            // Forward request off to backend with permissions token
            request.SetHeaders['X-CanDIG-Authz'] = 'Bearer ' + vault_data.data.token;
        } else {
            request.ReturnOverrides.ResponseCode = 403
            request.ReturnOverrides.ResponseError = "Vault Error"
        }
    }
    
    // MUST return both the request and session
    return permissionsStoreMiddleware.ReturnData(request, session.meta_data);
});

log("Permissions Store Middleware initialised");

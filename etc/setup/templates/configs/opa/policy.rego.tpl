package permissions

import input

now := time.now_ns()/1000000000

default allowed = false
default iss = "${TYK_PROVIDERS_ISSUER}"
default aud = "${KC_CLIENT_ID}"

default full_authn_pk=`-----BEGIN PUBLIC KEY-----
${KC_PUBLIC_KEY}
-----END PUBLIC KEY-----`

allowed = true {
    # retrieve authentication token parts
    [authN_token_header, authN_token_payload, authN_token_signature] := io.jwt.decode(input.kcToken)

    # retrieve authorization token parts
    [authZ_token_header, authZ_token_payload, authZ_token_signature] := io.jwt.decode(input.vaultToken)


    # Verify authentication token signature
    authN_token_is_valid := io.jwt.verify_rs256(input.kcToken, full_authn_pk)


    all([
        # Authentication
        authN_token_is_valid == true, 
        authN_token_payload.aud == aud, 
        authN_token_payload.iss == iss, 
        authN_token_payload.iat < now,
        
        # temp example; discriminate by user name
        ## authN_token_payload.preferred_username == "bob"

        # Authorization
        ##authZ_token_payload.aud == aud, 
        ##authZ_token_payload.iss == iss, 
        authZ_token_payload.iat < now,
    ])
}

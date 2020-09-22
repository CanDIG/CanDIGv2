package permissions

import input

now := time.now_ns()/1000000000

default allowed = false
default iss = "${TYK_PROVIDERS_ISSUER}"
default aud = "${KC_CLIENT_ID}"

default pk_header="-----BEGIN PUBLIC KEY-----"
default kc_public_key = "${KC_PUBLIC_KEY}"
default pk_footer="-----END PUBLIC KEY-----"

allowed = true {
    # retrieve authentication token parts
    [auth_token_header, auth_token_payload, auth_token_signature] := io.jwt.decode(input.kcToken)

    
    # temp example; discriminate by user name
    #auth_token_payload.preferred_username = "bob"


    # TODO: elaborate rules using authorization token
    #[authz_token_header, authz_token_payload, authz_token_signature] := io.jwt.decode(input.vaultToken)
    
    # ...

    # TODO: Verify signature
    #auth_token_is_valid := io.jwt.verify_rs256(input.kcToken, concat("", [pk_header, kc_public_key, pk_footer]))
    #auth_token_is_valid==true

    all([auth_token_payload.aud == aud, auth_token_payload.iss == iss, auth_token_payload.iat < now])
}

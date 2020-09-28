package permissions

import input

now := time.now_ns()/1000000000

default allowed = false

default iss = "http://keycloak:8081/auth/realms/candig"
default aud = "cq_candig"

default full_authn_pk=`-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvKv8wOGVAA4xEYLqENRCLxVvLYiN0TrDcpkj5kTTF2Vxm6q21sBREDI8Oog7QAghPhzTq7LxPv/871/4mQ+InzvSoUOh+2BEmDJgq2DKuh/Ka1EdDQO0D0gVuEX53gowf6RvmTHBGOJzIil0Xa29xZKV4S/eIKHxvyMQ8/YtwflL4PrGTwMuzTQk4v8sO8tjvigP1vcjKywDoGAqzGc/9xJepP57LqCjkq1EqySA8+BOu49cLQCzrLCJoezhCREgsgEKLU+JihJ8y4zwGnpG8pKS4eN47+9lLOopKvnorJJWPyX2Q0CWvUTknP1hxctokTzzNnMHkYh/Z4CDX99e/wIDAQAB
-----END PUBLIC KEY-----`

default full_authz_pk=`-----BEGIN PUBLIC KEY-----

-----END PUBLIC KEY-----`

default authz_jwks=`{"keys":[{"use":"sig","kty":"RSA","kid":"b0b2c88e-147c-7804-e42e-04ec67191d05","alg":"RS256","n":"y6F3PGXecDGrr2TUYIQiZJpAf63AO2ZLxk1e5AdrMykpUl9RM47cuwqo0gTBbGT_2lrpMCXaFS_JlBaZtzlTVuuuA8Vbhsm-hwkAF_iBV8o6Y5E_fCftGzhFNglfbD_g1hrSbAv6HJQ0VU-pzmWTDo-Kn3aaxKLW-DJs2ujU3sz2SAysWmoekCHzEV2zep1-EQcJ1e9U_oUq0Rn_BfHZebgiI9AgMWym5lAa_-Eq8ecVjXBu0mSmIJeaMFzFhKwdFt-qTO_1Wb9Ot1oPmR2y08ah7IZW8ZBY6GQku9jYjOsHEwZK5fjs_n9npPEx_bEzFAXpOaTf2TBRwirqsDBHrQ","e":"AQAB"}]}`

allowed = true {
    # retrieve authentication token parts
    [authN_token_header, authN_token_payload, authN_token_signature] := io.jwt.decode(input.kcToken)

    # retrieve authorization token parts
    [authZ_token_header, authZ_token_payload, authZ_token_signature] := io.jwt.decode(input.vaultToken)


    # Verify authentication token signature
    authN_token_is_valid := io.jwt.verify_rs256(input.kcToken, full_authn_pk)

    # Verify authentication token signature
    authZ_token_is_valid := io.jwt.verify_rs256(input.vaultToken, authz_jwks)


    all([
        # Authentication
        authN_token_is_valid == true, 
        authN_token_payload.aud == aud, 
        authN_token_payload.iss == iss, 
        authN_token_payload.iat < now,
        
        authN_token_payload.preferred_username == "bob",

        # Authorization
        authZ_token_is_valid == true,
        ##authZ_token_payload.aud == aud, 
        ##authZ_token_payload.iss == iss, 
        authZ_token_payload.iat < now,
    ])
}

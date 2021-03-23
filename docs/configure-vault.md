# Setup

Disclaimer: These are notes that were taken to build a PoC in a dev environment. To read the steps taken to provision
the user entitlements dynamically, see the `Makefile`'s `compose-authx-setup` command, and `./etc/setup/scripts/subtasks/vault_setup.sh`

## In dev

More convenient to listen on 0.0.0.0 (will include IPs and custom hosts,
since the client calling are inside docker containers).

```
vault server -dev -dev-listen-address=0.0.0.0:8200 -log-level=debug
```

Load env variables for convenience (the token is included in the server
output).

```
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN="..."
```

May also need to enable audit to see the logs...

```
vault audit enable file file_path=/tmp/vault-audit.log
```

## Configure vault to accept JWT tokens

Enable the plugin

```
vault auth enable jwt
```

Next, we need a policy (to give us access to some paths in vault):

```
vault policy write tyk vault-policy.hcl
```

In vault-policy.hcl there is:
```
path "identity/oidc/token/*" {
  capabilities = ["create", "read"]
}
```

Then we need a role to associate users authenticating with OIDC, here's
some more info regarding these fields:

 - user_claim: The name of the OIDC claim used to match with vault entities
(might change depending on your provider)
 - bound_audiences: Correspond to the OIDC client ID

```
vault write auth/jwt/role/researcher \
    user_claim=preferred_username \
    bound_audiences=cq_candig \
    role_type=jwt \
    policies=tyk \
    ttl=1h
```

Next we need to provide some information for vault to validate the JWT token.
Again the OIDC discovery url will change based on the provider, the url down below
is based on a setup such as with candig_compose & Keycloak.

If you are using a different OIDC provider, be aware that vault will want the 
URL without "/.well-known/openid-configuration/".

```
vault write auth/jwt/config \
    oidc_discovery_url="http://$CANDIG_DOMAIN_NAME:8081/auth/realms/candig" \ 
    bound_issuer="http://$CANDIG_DOMAIN_NAME:8081/auth/realms/candig" \
    default_role="researcher"
```

Warning! It might happen, when writing and overwriting such configuration,
that the command line tool will output errors like:

```
Failed to parse K=V data: invalid key/value pair " ": format must be key=value
```

In which case you can also write config into vault with such a format:
```
vault write auth/jwt/config -<<EOF
{
    "oidc_discovery_url":"http://$CANDIG_DOMAIN_NAME:8081/auth/realms/candig",
    "bound_issuer":"http://$CANDIG_DOMAIN_NAME:8081/auth/realms/candig",
    "default_role":"researcher"
}
EOF
```

## Create a user and give him entitlements

First off let's create a user ("entity" in vault's context), this is where
we keep the entitlements and other info to be consumed by services down the line.

```
vault write identity/entity -<<EOF
{
    "name": "potato",
    "metadata": {"dataset123": 4}
}
EOF
```

(Vault will return a list of values, you will need the "id" later on)

Next vault needs an alias to complete the link between the JWT and the entity.
To do so we need the mount accessor of our auth method:

```
vault auth list -format=json
# Should be in ["jwt"]["accessor"]
```

Do note the name of this alias will need to match the username of the OIDC provider
(e.g. the content of the preferred_username field in this current setup with KC).

And for the entity alias itself:

```
vault write identity/entity-alias -<<EOF
{
    "name": "potato",
    "mount_accessor": "$JWT_ACCESSOR_VALUE",
    "canonical_id": "$ENTITY_ID"
}
EOF
```

## Enable identity tokens from Vault

The last step will let vault create a JWT based on the entity we've just created.
To do so we first need a key:

```
vault write identity/oidc/key/test-key -<<EOF
{
    "rotation_period": "24h",
    "allowed_client_ids": ["cq_candig"]
}
EOF
```

Then we'll need a role to match the key and insert custom info in the JWT.
We might not want to dump the entire metadata field in the token, TBD.

```
vault write identity/oidc/role/researcher -<<EOF
{
    "key": "test-key",
    "client_id": "cq_candig",
    "template": "{\"permissions\": {{identity.entity.metadata}}}"
}
EOF
```

And voilà!

from dotenv import dotenv_values
import json
import os
import re
import tempfile


### Use this to handle getting env vars from the .env file; it will handle the differences between Make's .env format and python-dotenv's format.
# get_env_value returns the correct, interpolated value for a variable.
# get_env returns variables that are often exported for env vars, as well as several variables that come from generated secrets. All other values are saved as CANDIG_ENV.


CANDIGV2_ENV = None
INTERPOLATED_ENV = None
with open(".env") as f:
    envs = f.read().replace("define ", "").replace("endef", "")
    with tempfile.NamedTemporaryFile("w", delete=False) as fp:
        fp.write(envs)
    CANDIGV2_ENV = dotenv_values(fp.name, interpolate=False)
    INTERPOLATED_ENV = dotenv_values(fp.name, interpolate=True)
    os.unlink(fp.name)


# Python-dotenv doesn't interpolate quite correctly, so get_env_value interpolates manually
def get_env_value(key):
    raw_value = CANDIGV2_ENV[key]

    while True:
        var_match = re.match(r"^(.*)\$\{(.+?)\}(.*)$", raw_value, re.DOTALL)
        if var_match is not None:
            raw_value = var_match.group(1) + CANDIGV2_ENV[var_match.group(2)] + var_match.group(3)
        else:
            break

    CANDIGV2_ENV[key] = raw_value
    return raw_value


def get_env():
    vars = {}
    vars["CANDIG_URL"] = get_env_value("TYK_LOGIN_TARGET_URL")
    vars["CANDIG_CLIENT_ID"] = get_env_value("KEYCLOAK_CLIENT_ID")
    vars["KEYCLOAK_PUBLIC_URL"] = get_env_value("KEYCLOAK_PUBLIC_URL")
    vars["KEYCLOAK_REALM_URL"] = get_env_value("KEYCLOAK_REALM_URL")
    vars["VAULT_URL"] = get_env_value("VAULT_SERVICE_PUBLIC_URL")
    vars["OPA_URL"] = get_env_value("OPA_URL")
    vars["MINIO_URL"] = get_env_value("MINIO_PUBLIC_URL")
    vars["TYK_LOGIN_TARGET_URL"] = get_env_value("TYK_LOGIN_TARGET_URL")
    vars["TYK_POLICY_ID"] = get_env_value("TYK_POLICY_ID")
    vars["CANDIG_DEBUG_MODE"] = get_env_value("CANDIG_DEBUG_MODE")
    vars["CANDIG_USER_KEY"] = get_env_value("CANDIG_USER_KEY")

    # vars that come from files:
    with open(f"tmp/secrets/opa-service-token") as f:
        vars["OPA_SECRET"] = f.read().splitlines().pop()
    with open(f"tmp/secrets/keycloak-client-{vars['CANDIG_CLIENT_ID']}-secret") as f:
        vars["CANDIG_CLIENT_SECRET"] = f.read().splitlines().pop()
    if os.path.isfile("tmp/secrets/keycloak-test-site-admin"):
        with open(f"tmp/secrets/keycloak-test-site-admin") as f:
            vars["CANDIG_SITE_ADMIN_USER"] = f.read().splitlines().pop()
        with open(f"tmp/secrets/keycloak-test-site-admin-password") as f:
            vars["CANDIG_SITE_ADMIN_PASSWORD"] = f.read().splitlines().pop()
    with open(f"tmp/secrets/keycloak-test-user") as f:
        vars["CANDIG_NOT_ADMIN_USER"] = f.read().splitlines().pop()
    with open(f"tmp/secrets/keycloak-test-user-password") as f:
        vars["CANDIG_NOT_ADMIN_PASSWORD"] = f.read().splitlines().pop()
    with open(f"tmp/secrets/keycloak-test-user2") as f:
        vars["CANDIG_NOT_ADMIN_USER2"] = f.read().splitlines().pop()
    with open(f"tmp/secrets/keycloak-test-user2-password") as f:
        vars["CANDIG_NOT_ADMIN_PASSWORD2"] = f.read().splitlines().pop()
    with open(f"tmp/secrets/vault-s3-token") as f:
        vars["VAULT_S3_TOKEN"] = f.read().splitlines().pop()
    with open(f"tmp/vault/keys.txt") as f:
        vars["VAULT_ROOT_TOKEN"] = f.read().splitlines().pop(-1)
    with open(f"tmp/secrets/minio-access-key") as f:
        vars["MINIO_ACCESS_KEY"] = f.read().splitlines().pop()
    with open(f"tmp/secrets/minio-secret-key") as f:
        vars["MINIO_SECRET_KEY"] = f.read().splitlines().pop()
    with open(f"tmp/secrets/tyk-secret-key") as f:
        vars["TYK_SECRET_KEY"] = f.read().splitlines().pop()
    vars["POSTGRES_PASSWORD_FILE"] = f"tmp/secrets/metadata-db-secret"
    vars["CANDIG_ENV"] = INTERPOLATED_ENV
    vars["DB_PATH"] = "metadata-db"
    return vars


def main():
    vars = get_env()
    vars.pop('CANDIG_ENV')
    with open("env.sh", "w") as f:
        for key in vars.keys():
            f.write(f"export {key}={vars[key]}\n")

if __name__ == "__main__":
    main()

from dotenv import dotenv_values
import json
import os
import re
import tempfile

CANDIGV2_ENV = None
INTERPOLATED_ENV = None
with open(".env") as f:
    envs = f.read().replace("define ", "").replace("endef", "")
    with tempfile.NamedTemporaryFile("w", delete=False) as fp:
        fp.write(envs)
    CANDIGV2_ENV = dotenv_values(fp.name, interpolate=False)
    INTERPOLATED_ENV = dotenv_values(fp.name, interpolate=True)
    os.unlink(fp.name)


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
    vars["VAULT_URL"] = vars["CANDIG_URL"] + "/vault"
    vars["OPA_URL"] = vars["CANDIG_URL"] + "/policy"
    vars["OPA_SITE_ADMIN_KEY"] = get_env_value("OPA_SITE_ADMIN_KEY")
    vars["MINIO_URL"] = get_env_value("MINIO_PUBLIC_URL")
    vars["TYK_LOGIN_TARGET_URL"] = get_env_value("TYK_LOGIN_TARGET_URL")
    vars["TYK_POLICY_ID"] = get_env_value("TYK_POLICY_ID")

    # vars that come from files:
    with open(f"tmp/secrets/opa-root-token") as f:
        vars["OPA_SECRET"] = f.read().splitlines().pop()
    with open(f"tmp/secrets/keycloak-client-{vars['CANDIG_CLIENT_ID']}-secret") as f:
        vars["CANDIG_CLIENT_SECRET"] = f.read().splitlines().pop()
    with open(f"tmp/secrets/keycloak-test-user2") as f:
        vars["CANDIG_SITE_ADMIN_USER"] = f.read().splitlines().pop()
    with open(f"tmp/secrets/keycloak-test-user2-password") as f:
        vars["CANDIG_SITE_ADMIN_PASSWORD"] = f.read().splitlines().pop()
    with open(f"tmp/secrets/keycloak-test-user") as f:
        vars["CANDIG_NOT_ADMIN_USER"] = f.read().splitlines().pop()
    with open(f"tmp/secrets/keycloak-test-user-password") as f:
        vars["CANDIG_NOT_ADMIN_PASSWORD"] = f.read().splitlines().pop()
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
    vars["CANDIG_ENV"] = INTERPOLATED_ENV
    return vars


def main():
    vars = get_env()
    vars.pop('CANDIG_ENV')
    with open("env.sh", "w") as f:
        for key in vars.keys():
            f.write(f"export {key}={vars[key]}\n")

if __name__ == "__main__":
    main()

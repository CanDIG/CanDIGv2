from dotenv import dotenv_values

def main():
    candigv2_env = dotenv_values(f".env")

    vars = {}
    vars["CANDIG_URL"] = candigv2_env["TYK_LOGIN_TARGET_URL"]
    vars["CANDIG_CLIENT_ID"] = candigv2_env["KEYCLOAK_CLIENT_ID"]
    vars["KEYCLOAK_PUBLIC_URL"] = candigv2_env["KEYCLOAK_PUBLIC_URL"]
    vars["VAULT_URL"] = vars["CANDIG_URL"] + "/vault"
    vars["OPA_URL"] = vars["CANDIG_URL"] + "/policy"
    vars["OPA_SITE_ADMIN_KEY"] = candigv2_env["OPA_SITE_ADMIN_KEY"]
    vars["MINIO_URL"] = candigv2_env["MINIO_PUBLIC_URL"]

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

    with open("env.sh", "w") as f:
        for key in vars.keys():
            f.write(f"export {key}={vars[key]}\n")

if __name__ == "__main__":
    main()

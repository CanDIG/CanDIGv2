{
    "backend": {
      "file": {
        "path": ${VAULT_FILE_PATH}
      }
    },
    "listener": {
      "tcp":{
        "address": "${VAULT_SERVICE_HOST}:${VAULT_SERVICE_PORT}",
        "tls_disable": ${VAULT_TLS_DISABLE}
      }
    },
    "ui": ${VAULT_UI}
  }
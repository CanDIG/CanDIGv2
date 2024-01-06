#!/usr/bin/env bash

### Creates a key-value secret store for the service in Vault. This should be invoked at the end of the <service>_setup.sh script (see opa_setup.sh for an example).

### To access the secrets in the store, use the methods in the candigv2-authx package: set_service_store_secret and get_service_store_secret

set -x

source env.sh

vault=$(docker ps -a --format "{{.Names}}" | grep vault_1 | awk '{print $1}')

create_service_store() {
    local services=$@
    for service in $services
    do
        echo ">> setting up ${service} store"

        # get service's container IPs:
        local network_containers=$(docker network inspect candigv2_default | jq '.[0].Containers' | jq '[map(.Name), map(.IPv4Address)] | transpose | map( {(.[0]): .[1]}) | add')
        local ips=()
        if [ -n "$network_containers" ]; then
            gateway=$(docker network inspect --format "{{json .IPAM.Config}}" candigv2_default | jq '.[0].Gateway')
            gateway=$(echo ${gateway} | tr -d '"')
            ips=$(collect_ips $service)
            ips+="${gateway}/32"

            echo "create a policy for $service's access to the approle role and secret"
            docker exec $vault sh -c "echo 'path \"auth/approle/role/${service}/role-id\" {capabilities = [\"read\"]}' >> ${service}-policy.hcl; echo 'path \"auth/approle/role/${service}/secret-id\" {capabilities = [\"update\"]}' >> ${service}-policy.hcl; vault policy write ${service} ${service}-policy.hcl"

            echo "create an approle for $service"
            cmd="vault write auth/approle/role/${service} secret_id_ttl=10m token_ttl=20m token_max_ttl=30m token_policies=${service}"
            if [ $CANDIG_DEBUG_MODE -eq 0 ]; then
              cmd+=" secret_id_bound_cidrs=${ips} token_bound_cidrs=${ips}"
            fi
            docker exec $vault sh -c $cmd

            echo ">> setting up $service store policy"
            docker exec $vault sh -c "echo 'path \"${service}/*\" {capabilities = [\"create\", \"update\", \"read\", \"delete\"]}' >> ${service}-policy.hcl; vault policy write ${service} ${service}-policy.hcl"

            if [[ $service != "opa" ]]; then
                echo ">> add $service store to opa's policy"
                docker exec $vault sh -c "echo 'path \"${service}/*\" {capabilities = [\"create\", \"update\", \"read\", \"delete\"]}' >> opa-policy.hcl; vault policy write opa opa-policy.hcl"
            fi

            echo "save the role id to secrets"
            docker exec $vault sh -c "vault read -field=role_id auth/approle/role/${service}/role-id" > tmp/vault/$service-roleid

            echo "create a kv store for $service"
            docker exec $vault vault secrets enable -path=$service -description="${service} kv store" kv
        fi

        # get names of containers for service:
        local containers=$(cat lib/$service/docker-compose.yml | yq '.services' | jq  'keys' | jq -r @sh)
        for container in $containers
        do
            # copy roleid to container
            container=$(echo ${container} | tr -d "'")
            docker cp $PWD/tmp/vault/${service}-roleid candigv2_${container}_1:/home/candig/roleid
        done
        # if we're not in debug mode, delete the tmp roleid file
        if [[ ${CANDIG_DEBUG_MODE:-"0"} == "0" ]]; then
            rm $PWD/tmp/vault/{service}-roleid
        fi

    done
}

collect_ips() {
    local services=$@

    local ips=()
    for service in $services
    do
        # get names of containers for service:
        local containers=$(cat lib/$service/docker-compose.yml | yq '.services' | jq  'keys' | jq -r @sh)

        # get service's container IPs:
        local network_containers=$(docker network inspect candigv2_default | jq '.[0].Containers' | jq '[map(.Name), map(.IPv4Address)] | transpose | map( {(.[0]): .[1]}) | add')
        if [ -n "$network_containers" ]; then
            for container in $containers
            do
                container=$(echo ${container} | tr -d "'")
                local ip=$(echo $network_containers | jq --arg x "candigv2_${container}_1" -r '.[$x]')
                ip="${ip%16}32"
                ips+="\"$ip\","
            done
        fi
    done
    echo $ips
}


create_service_store $@

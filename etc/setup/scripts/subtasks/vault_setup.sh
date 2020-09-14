#! /bin/bash
# This script will set up a full vault environment on your local CanDIGv2 cluster


# vault-config.json
echo "Working on vault-config.json .."
mkdir ${PWD}/lib/vault/config
envsubst < ${PWD}/etc/setup/templates/configs/vault/vault-config.json.tpl > ${PWD}/lib/vault/config/vault-config.json

# boot container
docker-compose -f ${PWD}/lib/vault/docker-compose.yml up -d

# ssh into container
# example keys/tokens (TODO: automate)
KEY_1=5f1xhr4FdqobnMUmkoV2ewRhRGFXBQf+7DSjW8cgmvn+
KEY_2=oMcAdjCm2UITy0fcAqvNEpk7jnfc278XffXq7HQgSDll
KEY_3=TukMeCpJroaPF/4lEPOH2M8Cd/iX18nfsb7Pz8PAWX95
ROOT_LOGIN_TOKEN=s.Zlbes4X0ER3Eaym5MKmpHBCa
# --

# -- todo: run only if not already initialized --
# gather keys and login token
stuff=$(docker exec -it vault sh -c "vault operator init" | head -7 | rev | cut -d " " -f1 | rev)

echo "found stuff as ${stuff}"

declare -a key_array
key_count=1
max_keys=3
while IFS= read -r line ; do 

    if [[ max_keys -ge key_count  ]]; then
    
        key_array+=("${line}")
        #echo "found: ${key_array}"
    fi

    if [[ 7 -eq key_count  ]]; then
        ROOT_LOGIN_TOKEN=$line
        #echo "found root token: ROOT_LOGIN_TOKEN : $ROOT_LOGIN_TOKEN"; 
    fi
    #key_count=$(eval ($key_count+1))
    key_count=$(echo $(($key_count+1)))

done <<< "$stuff"

# unseal the vault
sleep 1
echo "${key_array[0]}"
sleep 1
echo "${key_array[1]}"
sleep 1
echo "${key_array[2]}"
sleep 1

# doesn't work yet ---
echo ">> unsealing vault with keys ${key_array[0]}, ${key_array[1]}, ${key_array[2]}"
sleep 1
export cmd1="vault operator unseal ${key_array[0]}" 
sleep 1
export cmd2="vault operator unseal ${key_array[1]}"
sleep 1
export cmd3="vault operator unseal ${key_array[2]}"
sleep 1

echo "set command to ${cmd1}"
sleep 1
echo "set command to ${cmd2}"
sleep 1
echo "set command to ${cmd3}"
sleep 1

result=$(docker exec -it -e RUN_ME="${cmd1}" vault sh -c "$(echo "run me is $RUN_ME")")
echo $result
sleep 1
docker exec -it -e RUN_ME="${cmd2}" vault sh -c "$RUN_ME"
sleep 1
docker exec -it -e RUN_ME="${cmd3}" vault sh -c "$RUN_ME"
sleep 1

# login
#echo ">> logging in with ${ROOT_LOGIN_TOKEN}"
#docker exec -it vault sh -c "vault login $ROOT_LOGIN_TOKEN"

# configuration
docker exec -it vault sh -c "vault audit enable file file_path=/tmp/vault-audit.log"
# ..
# ---


# sudo rm -r data/ ;sudo rm -r logs/ ; sudo rm -r policies/
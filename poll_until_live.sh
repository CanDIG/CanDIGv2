#!/usr/bin/env bash

# poll a url until it returns 200
url=$1
token=$2

cmd="curl -s -w \"%{http_code}\" ${url}"
if [[ $token != '' ]]; then
    cmd="${cmd}  -H \"Authorization: Bearer ${token}\""
    echo $cmd
fi

echo $cmd | bash &> .tmp_store
grep -q "200" .tmp_store
while [[ $? -ne 0 ]];
do
    sleep 2
    echo "..."
    echo $cmd | bash &> .tmp_store
    grep -q "200" .tmp_store
done
rm .tmp_store

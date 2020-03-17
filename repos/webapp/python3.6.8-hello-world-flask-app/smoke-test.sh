#!/bin/bash

if [ -n "${BASH_SOURCE}" ]
then
    dir_here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
else
    dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
fi
dir_tag="${dir_here}"
dir_repo="$(dirname ${dir_tag})"

repo_name=$(cat ${dir_repo}/repo-config.json | jq '.repo_name' -r)
tag_name=$(cat ${dir_tag}/tag-config.json | jq '.tag_name' -r)
container_name="${repo_name}-${tag_name}-smoke-test"

check_exit_status() {
    exit_status=$1
    if [ $exit_status != 0 ]
    then
        echo "FAILED!"
        docker container stop "${container_name}"
        exit $exit_status
    fi
}

local_port="29876"
container_port="29876"

docker run --rm -dt --name "${container_name}" -p $local_port:$container_port "${repo_name}:${tag_name}" "${container_port}"
sleep 2 # sleep 2 seconds wait web server become ready

echo "check if the web app successfully running locally"
curl "http://localhost:${local_port}"
check_exit_status $?
echo "yes"

# remove container if all success
docker container stop "${container_name}"

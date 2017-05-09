#!/bin/bash

API_NAME=party_api
API_VERSION=1.0.1
API_REPO=ras-party
API_URL=sdcplatform/party-api/1.0.1

curl https://api.swaggerhub.com/apis/sdcplatform/party-api/1.0.1


python3 generate_params.py sdcplatform-party-api-1.0.1-swagger.json
java -jar /usr/local/bin/swagger-codegen-cli.jar generate \
  -i sdcplatform-party-api-1.0.1-swagger.json \
  -l python-flask \
  -o ../ras-repos/ras-party



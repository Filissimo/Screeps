#!/bin/bash

token=$1

touch config.json
echo '{' >> config.json
echo '"token": "'$token'",' >> config.json
echo '"branch": "master",' >> config.json
echo '"ptr": false' >> config.json
echo '}' >> config.json
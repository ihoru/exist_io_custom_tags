#!/usr/bin/env bash

# Calling this script:
# ./scripts/virtualenv.sh

DIR=`dirname $0`;
cd ${DIR}/..;
virtualenv -p python3.6 ENV;

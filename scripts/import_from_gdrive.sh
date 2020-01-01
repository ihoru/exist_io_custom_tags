#!/usr/bin/env bash

DIR=`dirname $0`;
cd ${DIR}/..;
source $PWD/ENV/bin/activate;

python $PWD/import_from_gdrive.py >> logs/import_from_gdrive.log 2>&1;

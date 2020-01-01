#!/usr/bin/env bash

DIR=`dirname $0`;
cd ${DIR}/..;
source $PWD/ENV/bin/activate;
f=logs/import_from_gdrive.log;
date >> $f;
python $PWD/import_from_gdrive.py >> $f 2>&1;
date >> $f;

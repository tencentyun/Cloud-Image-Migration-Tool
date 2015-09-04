#!/bin/sh

. $(dirname $0)/env.sh

python ${SBIN_PATH}/main.py $LIB_PATH $CONF_PATH $LOG_PATH submit

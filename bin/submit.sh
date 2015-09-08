#!/bin/sh

. $(dirname $0)/env.sh

echo "submit.sh is running... "
python ${SBIN_PATH}/main.py $LIB_PATH $CONF_PATH $LOG_PATH submit
if [ $? -ne 0 ]; then
    echo "submit.sh failed. "
    exit 1
fi

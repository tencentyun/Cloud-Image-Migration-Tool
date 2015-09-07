#!/bin/sh

. $(dirname $0)/env.sh

if [ ! -f ${LOG_PATH}/jobs.db ]; then
    sh submit.sh
fi

db_is_consistent=$(sqlite3 ${LOG_PATH}/jobs.db 'SELECT (SELECT COUNT(*) FROM jobs) = (SELECT value FROM metadata WHERE key = "submitted");')
if [ $db_is_consistent != "1" ]; then
    echo "It seems that jobs database is in inconsistent state. "
    echo "Please run clean.sh to delete all jobs first. "
    exit 1
fi


echo "Start uploading..."
python ${SBIN_PATH}/main.py $LIB_PATH $CONF_PATH $LOG_PATH upload

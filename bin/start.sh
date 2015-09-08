#!/bin/sh

. $(dirname $0)/env.sh

submit_attempted=false

# database not exists
if [ ! -f ${LOG_PATH}/jobs.db ]; then
    sh submit.sh
    if [ $? -ne 0 ]; then exit 1; fi
    submit_attempted=true
fi

# database is in inconsistent mode, this should never happen
db_is_consistent=$(sqlite3 ${LOG_PATH}/jobs.db 'SELECT (SELECT COUNT(*) FROM jobs) = (SELECT value FROM metadata WHERE key = "submitted");')
if [ "$db_is_consistent" != "1" ]; then
    echo "It seems that jobs database is in inconsistent state. "
    echo "Please run clean.sh to delete all jobs first. "
    exit 1
fi

# enforce submitting
if [[ $# == 1 && $1 == "-f" && $submit_attempted != "true" ]]; then
    sh submit.sh
    if [ $? -ne 0 ]; then exit 1; fi
    submit_attempted=true
fi

# db is empty
db_num_jobs=$(sqlite3 ${LOG_PATH}/jobs.db 'SELECT value FROM metadata WHERE key = "submitted";')
if [ $db_num_jobs == "0" -a $submit_attempted == "false" ]; then
    sh submit.sh
    if [ $? -ne 0 ]; then exit 1; fi
    submit_attempted=true
fi

# still is empty 
db_num_jobs=$(sqlite3 ${LOG_PATH}/jobs.db 'SELECT value FROM metadata WHERE key = "submitted";')
if [ $db_num_jobs == "0" ]; then
    echo "Nothing to upload"
    exit 0
fi

echo "Start uploading..."
python ${SBIN_PATH}/main.py $LIB_PATH $CONF_PATH $LOG_PATH upload

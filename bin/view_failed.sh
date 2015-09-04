#!/bin/sh

. $(dirname $0)/env.sh

sqlite3 ${LOG_PATH}/jobs.db 'select fileid, log from jobs where status = 2;'

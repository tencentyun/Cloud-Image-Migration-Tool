#!/bin/sh

. $(dirname $0)/env.sh

sqlite3 ${LOG_PATH}/jobs.db 'SELECT fileid, log FROM jobs WHERE status = 2 ORDER BY serial;'

#!/bin/sh

. $(dirname $0)/env.sh

rm -f ${LOG_PATH}/pid
rm -f ${LOG_PATH}/jobs.db
rm -f ${LOG_PATH}/jobs.db-journal


#!/bin/sh

. $(dirname $0)/env.sh

sqlite3 ${LOG_PATH}/jobs.db \
'select key,value from metadata where key = "submitted" or key = "successful" or key = "failed";' |\
awk -F\| ' \
BEGIN { \
    submitted = 0; \
    successful = 0; \
    failed = 0; \
} \
{ \
    if ($1 == "submitted") \
        submitted = $2; \
    else if ($1 == "successful") \
        successful = $2; \
    else if ($1 == "failed") \
        failed = $2; \
} \
END { \
    print "failed, successful / submitted: " failed ", " successful " / " submitted; \
} \
'

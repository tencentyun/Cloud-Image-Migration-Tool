#!/bin/sh

. $(dirname $0)/env.sh

pid=$(cat ${LOG_PATH}/pid 2> /dev/null)

if [ -z $pid ]; then
    echo "Tool is not running. "
    exit 1
else
    echo kill -INT $pid
    kill -INT $pid
fi

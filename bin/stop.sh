#!/bin/sh
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Project: 
 #  Filename: stop.sh 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  5, 2015
 #  Time: 16:23:11
 #  Description: 
###############################################################################

LOG_PATH="../log/"

function get_abs_path() {
    (
    cd $(dirname $1)
    echo $PWD/$(basename $1)
    )
}

LOG_PATH=$(get_abs_path $LOG_PATH)

master_pid=$(head -n 1 ${LOG_PATH}/pid 2> /dev/null)
pids=$(cat ${LOG_PATH}/pid 2> /dev/null)

if [ -z $master_pid ]; then
    echo "pid log not found. "
    exit 1
fi

# forcely kill all processes 
# there is a risk of actions not logged and other unpredictability
# use this only when the other does not work
if [[ $# == 1 && $1 == "-f" ]]; then
    for pid in $pids; do
        echo kill $pid
        kill $pid
    done
else
# kill all processes
# all actions are ensured to be logged
# this is the same with killing with Ctrl + C
    echo kill -INT $master_pid
    kill -INT $master_pid
fi


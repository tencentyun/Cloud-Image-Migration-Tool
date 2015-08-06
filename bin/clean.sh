#!/bin/sh
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Project: 
 #  Filename: clean.sh 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  5, 2015
 #  Time: 17:46:20
 #  Description: clean logs
###############################################################################

LOG_PATH="../log/"

function get_abs_path() {
    (
    cd $(dirname $1)
    echo $PWD/$(basename $1)
    )
}

LOG_PATH=$(get_abs_path $LOG_PATH)


rm -f ${LOG_PATH}/pid
rm -f ${LOG_PATH}/stderr
rm -f ${LOG_PATH}/stdout
rm -f ${LOG_PATH}/state

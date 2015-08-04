#!/bin/sh
###############################################################################
 #  Project: 
 #  Filename: start.sh 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  3, 2015
 #  Time: 16:51:00
 #  Description: 
###############################################################################

SBIN_PATH="../usr/sbin/"
LIB_PATH="../usr/lib/"
CONF_PATH="../conf/config.ini"

function get_abs_path() {
    (
    cd $(dirname $1)
    echo $PWD/$(basename $1)
    )
}

LIB_PATH=$(get_abs_path $LIB_PATH)
CONF_PATH=$(get_abs_path $CONF_PATH)


python ${SBIN_PATH}/traverse.py $LIB_PATH $CONF_PATH

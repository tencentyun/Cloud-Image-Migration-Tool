#!/bin/sh
###############################################################################
 #  Project: 
 #  Filename: start.sh 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  3, 2015
 #  Time: 16:51:00
 #  Description: start
###############################################################################

. $(dirname $0)/env.sh

python ${SBIN_PATH}/traverse.py $LIB_PATH $CONF_PATH $LOG_PATH

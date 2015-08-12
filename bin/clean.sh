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

. $(dirname $0)/env.sh

rm -f ${LOG_PATH}/pid
rm -f ${LOG_PATH}/stderr
rm -f ${LOG_PATH}/stdout
rm -f ${LOG_PATH}/state

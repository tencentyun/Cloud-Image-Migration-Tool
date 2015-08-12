#!/bin/sh
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: 
 #  Filename: env.sh 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug 12, 2015
 #  Time: 09:36:25
 #  Description: runtime environment
###############################################################################

SBIN_PATH="../usr/sbin/"
LIB_PATH="../usr/lib/"
CONF_PATH="../conf/config.ini"
LOG_PATH="../log/"

function get_abs_path() {
    (
    cd $(dirname $0)
    cd $(dirname $1)
    echo $PWD/$(basename $1)
    )
}

SBIN_PATH=$(get_abs_path $SBIN_PATH)
LIB_PATH=$(get_abs_path $LIB_PATH)
CONF_PATH=$(get_abs_path $CONF_PATH)
LOG_PATH=$(get_abs_path $LOG_PATH)



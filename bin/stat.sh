#!/bin/sh
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: 
 #  Filename: stat.sh 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  6, 2015
 #  Time: 10:31:47
 #  Description: show status
###############################################################################

LOG_PATH="../log/"

function get_abs_path() {
    (
    cd $(dirname $0)
    cd $(dirname $1)
    echo $PWD/$(basename $1)
    )
}

LOG_PATH=$(get_abs_path $LOG_PATH)

tail -f ${LOG_PATH}/state

#!/bin/sh
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: 
 #  Filename: get_failed.sh 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug 12, 2015
 #  Time: 09:44:43
 #  Description: show failed jobs
###############################################################################

. $(dirname $0)/env.sh


if [ -f ${LOG_PATH}/stderr ]; then
    cat ${LOG_PATH}/stderr
fi


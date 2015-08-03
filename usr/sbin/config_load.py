#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: 
 #  Filename: config_load.py 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  3, 2015
 #  Time: 17:12:54
 #  Description: 
###############################################################################

import ConfigParser

# TODO: case insensitive

def load_config(filename):
    config = ConfigParser.ConfigParser()
    config.read(filename)
    
    result = dict()

    for section in config.sections():
        result[section] = dict()
        for option in config.options(section):
            result[section][option] = config.get(section, option)

    return result 

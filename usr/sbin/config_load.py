#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Project: 
 #  Filename: config_load.py 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  3, 2015
 #  Time: 17:12:54
 #  Description: load ini file
 #               node that section and options names are case insensitive
###############################################################################

import ConfigParser


# section and option names are case insensitive
def load_config(filename):
    config = ConfigParser.ConfigParser()
    config.read(filename)
    
    result = dict()

    for section in config.sections():
        result[section.lower()] = dict()
        for option in config.options(section):
            result[section.lower()][option.lower()] = config.get(section, option)

    return result 

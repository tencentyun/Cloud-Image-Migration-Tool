#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Tencent Inc.
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: Cloud Image Migration Tool
 #  Filename: config_loader.py
 #  Version: 2.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Sep  7, 2015
 #  Time: 14:29:44
###############################################################################

import ConfigParser

class ConfigLoader(object):
    @staticmethod
    def load(filename):
        """
        Load file configuration into a second-level nested dict.

        Args:
            filename: Filename of the config file

        Returns:
            result: A second-level nested dict. The outer dict maps section 
                name to a inner dict. The inner dict maps property name to 
                property value.

        """
        config = ConfigParser.ConfigParser()
        config.read(filename)

        result = dict()

        for section in config.sections():
            result[section.lower()] = dict()
            for option in config.options(section):
                if config.get(section, option):
                    result[section.lower()][option.lower()] = config.get(section, option)

        return result

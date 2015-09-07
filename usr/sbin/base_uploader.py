#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Tencent Inc.
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: Cloud Image Migration Tool
 #  Filename: base_uploader.py
 #  Version: 2.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Sep  7, 2015
 #  Time: 14:29:44
 #  Description: base class of uploader
###############################################################################

import abc

class BaseUploader(object):
    __metaclass__ = abc.ABCMeta

    mandatory_options = []

    def __init__(self, config):
        self.config = config

    @staticmethod
    def check_config(config):
        for section, option in BaseUploader.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

    @abc.abstractmethod
    def upload(self, job):
        """
        type job: (fileid, source)
        rtype: (new fileid, status, log)

        do not throw any exception
        """
        pass


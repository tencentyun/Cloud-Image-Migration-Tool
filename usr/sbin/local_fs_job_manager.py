#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Tencent Inc.
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: Cloud Image Migration Tool
 #  Filename: local_fs_job_manager.py
 #  Version: 2.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Sep  7, 2015
 #  Time: 14:29:44
###############################################################################

from base_job_manager import BaseJobManager

import os

class LocalFSJobManager(BaseJobManager):
    """
    Derived class of BaseJobManager.
    Traverse local files and submit.

    Attributes:
        mandatory_options: Configuration options required by this class. This is
            a list of tuples each of which contains two strings, section name and 
            property name, both of which are case-insensitive.
    """

    mandatory_options = [
        ("local", "local.image_root_path"),
                        ]

    def __init__(self, config):
        """
        Initialize base class.
        """
        super(LocalFSJobManager, self).__init__(config)

    @staticmethod
    def check_config(config):
        """
        Check whether all required options are provided. 
        Also check the validity of some options.

        Args:
            config: configuration dict

        Returns:
            Returns string containing error message if there are some errors.
            Returns none otherwise.
        """
        for section, option in LocalFSJobManager.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        if not os.path.isabs(config["local"]["local.image_root_path"]):
            return "Error: Image root path %s is not absolute path. " % config["local"]["local.image_root_path"]

        if not os.path.isdir(config["local"]["local.image_root_path"]):
            return "Error: Image root path %s is not directory. " % config["local"]["local.image_root_path"]


    def do(self):
        """
        Implementation of abstract method.
        Traverse a directory and submit each file, with relative path as its
        file id and absolute path as its src.
        """

        image_root_path = self.config["local"]["local.image_root_path"]

        for dirpath, dirs, files in os.walk(image_root_path, followlinks = True):
            for filename in files:
                full_name = os.path.join(dirpath, filename)
                fileid = os.path.relpath(full_name, image_root_path)
                
                self.submit(fileid, "file://%s" % full_name)


#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Tencent Inc.
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: Cloud Image Migration Tool
 #  Filename: url_list_job_manager.py
 #  Version: 2.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Sep  7, 2015
 #  Time: 14:29:44
###############################################################################

from base_job_manager import BaseJobManager

import os
import urlparse

class URLListJobManager(BaseJobManager):
    """
    Derived class of BaseJobManager.
    Traverse a file consisting of a list of ULRs, one per line.

    Attributes:
        mandatory_options: Configuration options required by this class. This is
            a list of tuples each of which contains two strings, section name and 
            property name, both of which are case-insensitive.
    """

    mandatory_options = [
        ("urllist", "url.url_list_file_path"),
                        ]

    def __init__(self, config):
        super(URLListJobManager, self).__init__(config)


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
 
        for section, option in URLListJobManager.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        if not os.path.isabs(config["urllist"]["url.url_list_file_path"]):
            return "Error: URL list file %s is not absolute path. " % config["urllist"]["url.url_list_file_path"]

        if not os.path.isfile(config["urllist"]["url.url_list_file_path"]):
            return "Error: URL list %s is not regular file. " % config["urllist"]["url.url_list_file_path"]

    # implementation of abstract method
    def do(self):
        """
        Implementation of abstract method.
        Traverse a file consisting of a list of URLs and submit each URL, with
        path component of the URL as file id of the job and the whole URL as src.
        """

        file_handler = open(self.config["urllist"]["url.url_list_file_path"])

        for line in file_handler:
            url = line.strip()
            if len(url) == 0: continue

            fileid = urlparse.urlparse(url).path
            if len(fileid) and fileid[0] == '/':
                fileid = fileid[1: ]

            self.submit(fileid, url)

        file_handler.close()


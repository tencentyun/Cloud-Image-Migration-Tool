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
###############################################################################

import abc

class BaseUploader(object):
    """
    Abstract base class of uploader.
    This module is only used in the precedure of uploading.
    The abstract interface upload() accepts a job, uploads it somewhere and returns log.

    Attributes:
        mandatory_options: Configuration options required by this class. This is
            a list of tuples each of which contains two strings, section name and 
            property name, both of which are case-insensitive.

        config: Copy of configuration
    """

    __metaclass__ = abc.ABCMeta

    mandatory_options = []

    def __init__(self, config):
        """
        Initialize attributes. 
        """
        self.config = config

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
     
        for section, option in BaseUploader.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

    @abc.abstractmethod
    def upload(self, job):
        """
        Interface which should be implemented in derived class.

        Args:
            job: a tuple of (fileid, source)
                fileid: string, file id of this job
                source: undefined type, data to be uploaded, could be a filename 
                    or binary data or in any other forms

        Returns: 
            log: a tuple of (fileid, status, log)
                fileid: string, new file id of the job, could be same or different 
                    with that in argument
                status: integer, new status of the job, 0 -- new submitted, 1 -- successful, 2 -- faled.
                log: log in string

        Raises:
            DO NOT raise any exception in this function.

        """
        pass


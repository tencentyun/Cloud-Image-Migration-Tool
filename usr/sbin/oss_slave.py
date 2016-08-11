#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Tencent Inc.
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: Cloud Image Migration Tool
 #  Filename: oss_slave.py
 #  Version: 2.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Sep  7, 2015
 #  Time: 14:29:44
###############################################################################

from __future__ import print_function
from base_slave import BaseSlave
import urlparse
import oss2

class OssSlave(BaseSlave):
    """
    Derived class of BaseSlave.
    Retrieve a resource from Oss and send it along with file id to uploader.

	Attributes:
        mandatory_options: Configuration options required by this class. This is
            a list of tuples each of which contains two strings, section name and 
            property name, both of which are case-insensitive.
    """

    mandatory_options = [
        ("oss", "oss.accesskey"),
        ("oss", "oss.secretkey"),
        ("oss", "oss.bucket"),
        ("oss", "oss.endpoint"),
        ("oss", "oss.iscname"),
                        ]
    """
    Attributes:
        uploader_class: uploader class instance
    """
    def __init__(self, config, UploaderClass):
        """
        Initialize base class and uploader class instance.

        Args:
            config: configuration dict
            UploaderClass: uploader class
        """
        super(OssSlave, self).__init__(config)
        self.uploader_class = UploaderClass(config)

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
 
        for section, option in OssSlave.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        if config["oss"]["oss.iscname"].lower() not in [ "true", "false", "0", "1", "t", "f", "yes", "no", "y", "n" ]:
            return "Error: Invalid oss.oss.iscname. "

    def do_job(self, job):
        """
        Implementation of abstract method.
        Download the file and send the downloaded data along with file id to uploader.
        
        Args:
            job: a tuple of (index, fileid, old_status, source)
                index: integer, serial number of the job
                fileid: string, file id of the job
                old_status: integer, old status of the job. 0 -- new submitted, 1 -- successful, 2 -- failed
                source: string, source of the job

        Returns:
            log: a tuple of (index, fileid, old_status, new_status, log)
                index: keep the same with that in argument job
                fileid: string, new file id of the job, could be same or different 
                    with that in argument
                old_status: keep the same with that in argument
                new_status: integer, new status of the job
                log: log in string

        Raises:
            DO NOT raise any exception in this function.
        """
		
        access_key = self.config["oss"]["oss.accesskey"]
        secret_key = self.config["oss"]["oss.secretkey"]
        bucket_name = self.config["oss"]["oss.bucket"]
        endpoint = self.config["oss"]["oss.endpoint"]
        is_cname = self.config["oss"]["oss.iscname"].lower() in [ "true", "1", "t", "yes", "y" ]
        if "oss" in self.config and "oss.referer" in self.config["oss"]:
            referer = self.config["oss"]["oss.referer"]
        else:
            referer = None

        auth = oss2.Auth(access_key, secret_key)
        mybucket = oss2.Bucket(auth, endpoint, bucket_name, is_cname)
 
        serial = job[0]
        fileid = job[1]
        old_status = job[2]
        
        # read source
        status, log = None, None
        try:
            header=None
            if referer:
                header = {'Referer': referer}

            result = mybucket.get_object(fileid, headers=header)
            src = result.read()
        except Exception as e:
            status = 2
            log = str(e)
            

        if not status and not log:
            (new_fileid, status, log) = self.uploader_class.upload((fileid, src))
        else:
            new_fileid = fileid

        return (serial, new_fileid, old_status, status, log)


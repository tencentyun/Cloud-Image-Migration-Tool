#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Tencent Inc.
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: Cloud Image Migration Tool
 #  Filename: oss_job_manager.py
 #  Version: 2.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Sep  7, 2015
 #  Time: 14:29:44
###############################################################################

from base_job_manager import BaseJobManager

import os
import urlparse
import oss2

class OssJobManager(BaseJobManager):
    """
    Derived class of BaseJobManager.
    Traverse a oss account.

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
    def __init__(self, config):
        """
        Initialize base class.
        """
        super(OssJobManager, self).__init__(config)

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
 
        for section, option in OssJobManager.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        if config["oss"]["oss.iscname"].lower() not in [ "true", "false", "0", "1", "t", "f", "yes", "no", "y", "n" ]:
            return "Error: Invalid oss.oss.iscname. "

    def do(self):
        """
        Implementation of abstract method.
        Traverse a Oss account and submit each file.
        File id of the job is key of the Oss file.
        Src is download URL of the resource. 
        If resource requires a referer to download, the referer is also included
        in src, which is seperated by a tab with download URL.
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

        def get_list_object(bucket, prefix) :
            marker = ''
            trytime = 2
            while True:
                try:
                    lor=bucket.list_objects(prefix=prefix, marker=marker, max_keys=100)
                except Exception as e:
                    trytime-=1
                    if trytime <= 0:
                        raise e
                    continue
                trytime = 2
                if lor.object_list:
                    for object in lor.object_list:
                        if object.is_prefix():
                            continue
                        elif object.key.endswith('/'):
                            continue
                            #if object.key.strip('/') != prefix.strip('/'):
                            #    get_list_object(bucket, object.key)
                        else:
                            self.submit(object.key, '')
                            		
                if not lor.is_truncated:
                    break
                else:
                    marker = lor.next_marker
		
        get_list_object(mybucket, '')

#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Tencent Inc.
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: Cloud Image Migration Tool
 #  Filename: qiniu_job_manager.py
 #  Version: 2.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Sep  7, 2015
 #  Time: 14:29:44
###############################################################################

from base_job_manager import BaseJobManager

import os
import urlparse
import qiniu

class QiniuJobManager(BaseJobManager):
    """
    Derived class of BaseJobManager.
    Traverse a Qiniu account.

    Attributes:
        mandatory_options: Configuration options required by this class. This is
            a list of tuples each of which contains two strings, section name and 
            property name, both of which are case-insensitive.
    """


    mandatory_options = [
        ("qiniu", "qiniu.accesskey"),
        ("qiniu", "qiniu.secretkey"),
        ("qiniu", "qiniu.bucket"),
        ("qiniu", "qiniu.domain"),
        ("qiniu", "qiniu.isprivate"),
                        ]
    def __init__(self, config):
        """
        Initialize base class.
        """
        super(QiniuJobManager, self).__init__(config)

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
 
        for section, option in QiniuJobManager.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        if config["qiniu"]["qiniu.isprivate"].lower() not in [ "true", "false", "0", "1", "t", "f", "yes", "no", "y", "n" ]:
            return "Error: Invalid Qiniu.qiniu.isprivate. "

    def do(self):
        """
        Implementation of abstract method.
        Traverse a Qiniu account and submit each file.
        File id of the job is key of the Qiniu file.
        Src is download URL of the resource. 
        If resource requires a referer to download, the referer is also included
        in src, which is seperated by a tab with download URL.
        """

        access_key = self.config["qiniu"]["qiniu.accesskey"]
        secret_key = self.config["qiniu"]["qiniu.secretkey"]
        bucket_name = self.config["qiniu"]["qiniu.bucket"]
        domain = self.config["qiniu"]["qiniu.domain"]
        is_private = self.config["qiniu"]["qiniu.isprivate"].lower() in [ "true", "1", "t", "yes", "y" ]
        if "qiniu" in self.config and "qiniu.referer" in self.config["qiniu"]:
            referer = self.config["qiniu"]["qiniu.referer"]
        else:
            referer = None

        qn = qiniu.Auth(access_key, secret_key)
        bucket = qiniu.BucketManager(qn)

        marker = None
        eof = False
        while eof is False:
            (ret, eof, info) = bucket.list(bucket_name, prefix = None, marker = marker, limit = None)
            marker = ret.get("marker", None)
            for item in ret["items"]:
                fileid = item["key"].encode("utf-8")
                url = urlparse.urljoin(domain, fileid)

                if is_private:
                    url = qn.private_download_url(url, expires = 3600 * 24 * 365)

                if referer:
                    self.submit(fileid, url + "\t" + referer)
                else:
                    self.submit(fileid, url)
        if eof is not True:
            # error
            pass

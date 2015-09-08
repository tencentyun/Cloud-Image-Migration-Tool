#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Tencent Inc.
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: Cloud Image Migration Tool
 #  Filename: url_slave.py
 #  Version: 2.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Sep  7, 2015
 #  Time: 14:29:44
###############################################################################

from __future__ import print_function
from base_slave import BaseSlave
import urlparse
import urllib
import urllib2

class URLSlave(BaseSlave):
    """
    Derived class of BaseSlave.
    Retrieve a resource via URL and send it along with file id to uploader.

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
        super(URLSlave, self).__init__(config)
        self.uploader_class = UploaderClass(config)
    

    def openURL(self, url, referer):
        req = urllib2.Request(url)
        if referer:
            req.add_header("Referer", referer)
        r = urllib2.urlopen(req) 

        return (req.get_code(), r.read())

    def do_job(self, job):
        """
        Implementation of abstract method.
        Download the URL and send the downloaded data along with file id to uploader.
        
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
 
        serial = job[0]
        fileid = job[1]
        old_status = job[2]
        src = job[3].split("\t")

        url = src[0]
        referer = src[1] if len(src) > 1 else None
        
        # read source
        status, log = None, None
        try:
            # encode URL
            url_split_result = list(urlparse.urlsplit(url))
            url_split_result[2] = urllib.quote(url_split_result[2])
            url = urlparse.urlunsplit(url_split_result)

            req = urllib2.Request(url)
            if referer:
                req.add_header("Referer", referer)

            r = urllib2.urlopen(req)

            if r.getcode() is None or 100 <= r.getcode() < 400:
                src = r.read()
            else:
                status = 2
                log = "HTTP response status code: %d" % r.getcode()
        except Exception as e:
            status = 2
            log = str(e)
            

        if not status and not log:
            (new_fileid, status, log) = self.uploader_class.upload((fileid, src))
        else:
            new_fileid = fileid

        return (serial, new_fileid, old_status, status, log)


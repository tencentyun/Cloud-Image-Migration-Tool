#!/usr/bin/env python

from __future__ import print_function
from base_slave import BaseSlave
import urlparse
import urllib
import urllib2

class URLSlave(BaseSlave):
    def __init__(self, config, UploaderClass):
        super(URLSlave, self).__init__(config)
        self.uploader_class = UploaderClass(config)
    

    def openURL(self, url, referer):
        req = urllib2.Request(url)
        if referer:
            req.add_header("Referer", referer)
        r = urllib2.urlopen(req) 

        return (req.get_code(), r.read())

    # implementation of abstract method
    def do_job(self, job):
        """
        type job: (index, fileid, old_status, source)
        rtype: (index, new fileid, old_status, new_status, log)
        
        do not throw any exception
        """
 
        serial = job[0]
        fileid = job[1]
        old_status = job[2]
        src = job[3].split("\t")

        url = src[0]
        referer = src[1] if len(src) > 1 else None
        
        # read source
        # TODO: what if redirection
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

            if r.getcode() is None or 100 <= r.getcode() < 300:
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


#!/usr/bin/env python

#from __future__ import print_function
from base_slave import BaseSlave
import urlparse
import urllib
import urllib2
import platform

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
        type job: (index, fileid, source)
        rtype: (index, new fileid, status, log)
        
        do not throw any exception
        """
        serial = job[0]
        fileid = job[1]
        src = job[2].split("\t")

        url = src[0]
        referer = src[1] if len(src) > 1 else None
        
        # read source
        # TODO: test for file: ftp: http: https:
        # TODO: redirection
        # TODO: %20 problem
        status, log = None, None
        try:
            # encode URL
            url = urlparse.urlunsplit(map(lambda i: urllib.quote(i), urlparse.urlsplit(url)))

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

        return (serial, new_fileid, status, log)


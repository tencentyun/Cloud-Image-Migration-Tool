#!/usr/bin/env python

from __future__ import print_function
from base_slave import BaseSlave

class URLSlave(BaseSlave):
    def __init__(self, config, UploaderClass):
        super(URLSlave, self).__init__(config)
        self.uploader_class = UploaderClass(config)

    # implementation abstract method
    def do_job(self, job):
        """
        type job: (index, fileid, source)
        rtype: (index, new fileid, status, log)
        
        do not throw any exception
        """
        serial = job[0]
        fileid = job[1]
        src = job[2]
        
        # TODO: read source

        (new_fileid, status, log) = self.uploader_class.upload((fileid, src))

        return (serial, new_fileid, status, log)


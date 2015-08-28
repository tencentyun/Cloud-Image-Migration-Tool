#!/usr/bin/env python

from __future__ import print_function
from base_slave import BaseSlave
import time

class URLSlave(BaseSlave):
    def __init__(self, config):
        super(URLSlave, self).__init__(config)

    def do_job(self, job):
        print("get job:", job)
        #time.sleep(0.5)
        return (job[0], job[1], 1, None)

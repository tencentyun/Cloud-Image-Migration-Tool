#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Tencent Inc.
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: Cloud Image Migration Tool
 #  Filename: base_slave.py
 #  Version: 2.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Sep  7, 2015
 #  Time: 14:29:44
 #  Description: base class of slave
###############################################################################

import os
import abc
import signal


class BaseSlave(object):
    __metaclass__ = abc.ABCMeta 

    mandatory_options = [ ]

    def __init__(self, config):
        self.interrupted = False
        self.config = config

    @staticmethod
    def check_config(config):
        for section, option in BaseSlave.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        return None

    @abc.abstractmethod
    def do_job(self, job):
        """
        type job: (index, fileid, old_status, source)
        rtype: (index, new fileid, old_status, new_status, log)
        
        do not throw any exception
        """
        pass


    def start(self, job_queue, log_queue):
        def sigint_handler(signum, frame):
            self.interrupted = True
        signal.signal(signal.SIGINT, sigint_handler)
    
        while True:
            if self.interrupted:
                log_queue.put("quit")
                break

            job = job_queue.get()

            if job == "no more jobs":
                self.interrupted = True
            else:
                log_queue.put(self.do_job(job))



#!/usr/bin/env python

from __future__ import print_function
import os
import abc
import signal


class BaseSlave(object):
    __metaclass__ = abc.ABCMeta 

    mandatory_options = [ ]

    def __init__(self, config):
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


    def start(self, job_queue, log_queue, no_more_jobs):
        while True:
            if no_more_jobs.value == 1:
                job = "no more jobs"
            else:
                job = job_queue.get()

            if job == "no more jobs":
                log_queue.put("quit")
                break
            else:
                log_queue.put(self.do_job(job))



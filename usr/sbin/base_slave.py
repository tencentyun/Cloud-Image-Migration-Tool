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
###############################################################################

import os
import abc
import signal


class BaseSlave(object):
    """ 
    Abstract base class of slave.
    This module is only used in the precedure of uploading.
    The start() function runs in multiple processes. Each process accepts jobs,
    each of which is identified by a file id and a src. The process then retrieves 
    resource via the src and processes the resource in a certain way defined in 
    do_job() function. 

    Attributes:
        mandatory_options: Configuration options required by this class. This is
            a list of tuples each of which contains two strings, section name and 
            property name, both of which are case-insensitive.

        config: Copy of configuration

        interrupted: This value is initialized to False and is asynchronously
            set to True on receiving SIGINT. Slave will no longer fetch job from
            queue and prepare to quit after this value is set to True.
    """
        
    __metaclass__ = abc.ABCMeta 

    mandatory_options = [ ]

    def __init__(self, config):
        """
        Initialize some attributes.
        
        Args:
            config: configuration dict.
        """
        self.interrupted = False
        self.config = config

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
        for section, option in BaseSlave.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        return None

    @abc.abstractmethod
    def do_job(self, job):
        """
        Interface which should be implemented in derived class.
        
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
        pass


    def start(self, job_queue, log_queue):
        """
        Fetch jobs from job queue and send each job to do_job() function, which 
        should be implemented in derived class. 
        Put what do_job() function returns to log queue.

        Attributes:
            job_queue: Queue used to distribute jobs to slaves. Master process puts
                jobs into this queue and slaves fetch jobs from here.

            log_queue: Queue used to gather logs from slaves to master. Slave processes 
                put logs into this queue and master process fetches logs from here.

        """
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



#!/usr/bin/env python

import abc

class BaseUploader(object):
    __metaclass__ = abc.ABCMeta

    mandatory_options = []

    def __init__(self, config):
        self.config = config

    @staticmethod
    def check_config(config):
        for section, option in BaseUploader.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

    @abc.abstractmethod
    def upload(self, job):
        """
        type job: (fileid, source)
        rtype: (new fileid, status, log)

        do not throw any exception
        """
        pass


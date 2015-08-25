#!/usr/bin/env python

import abc


class JobManager(object):
    __metaclass__ = abc.ABCMeta

    mandatory_options = [
                          ("migrateinfo", "migrate.type"),
                        ]

    def __init__(self, config):
        self.config = config
        # TODO
        # init db

    @staticmethod
    def check_config(config):
        for section, option in JobManager.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        return None

    def submit(fileid, src):
        pass




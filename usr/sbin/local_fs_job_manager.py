#!/usr/bin/env python

from job_manager import JobManager

import os

class LocalFSJobManager(JobManager):

    mandatory_options = [
                          ("local", "local.image_root_path"),
                        ]


    def __init__(self, config):
        self.config = config
        super(LocalFSJobManager, self).__init__(config)


    @staticmethod
    def check_config(config):
        for section, option in JobManager.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        # TODO: can a single file be traversed?
        if not os.path.exists(config["local"]["local.image_root_path"]):
            return "Error: Image root path %s does not exist. "

        return None



    def do(self):
        pass




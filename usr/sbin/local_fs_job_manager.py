#!/usr/bin/env python

from __future__ import print_function

from job_manager import JobManager

import os

class LocalFSJobManager(JobManager):

    mandatory_options = [
        ("local", "local.image_root_path"),
                        ]

    def __init__(self, config):
        super(LocalFSJobManager, self).__init__(config)


    @staticmethod
    def check_config(config):
        for section, option in JobManager.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        if not os.path.isabs(os.path.expanduser(config["local"]["local.image_root_path"])):
            return "Error: Image root path %s is not absolute path. "

        if not os.path.isdir(config["local"]["local.image_root_path"]):
            return "Error: Image root path %s is not directory. "

        return None

    def do(self):
        image_root_path = self.config["local"]["local.image_root_path"]

        for dirpath, dirs, files in os.walk(image_root_path, followlinks = True):
            for filename in files:
                full_name = os.path.join(dirpath, filename)
                fileid = os.path.relpath(full_name, image_root_path)
                
                self.submit(fileid, "file://%s" % full_name)


#!/usr/bin/env python

from base_job_manager import BaseJobManager

import os

class LocalFSJobManager(BaseJobManager):

    mandatory_options = [
        ("local", "local.image_root_path"),
                        ]

    def __init__(self, config):
        super(LocalFSJobManager, self).__init__(config)


    @staticmethod
    def check_config(config):
        for section, option in LocalFSJobManager.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        if not os.path.isabs(config["local"]["local.image_root_path"]):
            return "Error: Image root path %s is not absolute path. " % config["local"]["local.image_root_path"]

        if not os.path.isdir(config["local"]["local.image_root_path"]):
            return "Error: Image root path %s is not directory. " % config["local"]["local.image_root_path"]


    # implementation of abstract method
    def do(self):
        image_root_path = self.config["local"]["local.image_root_path"]

        for dirpath, dirs, files in os.walk(image_root_path, followlinks = True):
            for filename in files:
                full_name = os.path.join(dirpath, filename)
                fileid = os.path.relpath(full_name, image_root_path)
                
                self.submit(fileid, "file://%s" % full_name)


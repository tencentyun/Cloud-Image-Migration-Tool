#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Project: 
 #  Filename: traverse_dir.py 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  4, 2015
 #  Time: 12:22:42
 #  Description: 
###############################################################################

from __future__ import print_function
import re
import os


def traverse(config):
    from job_queue import JobQueue
    # check config
    mandatory_options = [ 
                          ("MigrateInfo", "migrate.type"),
                          ("Local", "local.image_root_path"), 
                          ("AppInfo", "appinfo.appid"), 
                          ("AppInfo", "appinfo.secretid"),
                          ("AppInfo", "appinfo.secretkey"),
                          ("AppInfo", "appinfo.bucket"),
                          ("ToolConfig", "concurrency")
                        ] 

    for section, option in mandatory_options:
        if section not in config or option not in config[section]:
            print("Error: Option", section + "." + option, "is required. ")
            exit(1)

    if not os.path.isabs(config["Local"]["local.image_root_path"]):
        print("Error: Image root path", config["Local"]["local.image_root_path"], "is not absolute path")
        exit(1)
    
    # only filenames matching this regex will be uploaded, others would be ignored
    filename_pattern = re.compile(".*\.(?:jpg|jpeg|png|gif|bmp|webp)$", re.IGNORECASE)
    # use this to match all filenames
    # filename_pattern = None

    
    image_root_path = os.path.abspath(os.path.expanduser(config["Local"]["local.image_root_path"]))

    job_queue = JobQueue(
                         int(config["ToolConfig"]["concurrency"]),
                         config["AppInfo"]["appinfo.appid"],
                         config["AppInfo"]["appinfo.bucket"],
                         config["AppInfo"]["appinfo.secretid"],
                         config["AppInfo"]["appinfo.secretkey"]
                        )
     
    # traverse dir
    for dirpath, dirs, files in os.walk(image_root_path):
        for filename in files:
            if filename_pattern and not filename_pattern.match(filename):
                continue
            full_name = os.path.join(dirpath, filename)
            # TODO: fileid cannot contain . / and so on
            fileid = full_name[len(image_root_path) + 1: full_name.find(".")]
            # print(full_name, ":", fileid)

            job_queue.inqueue(0, full_name, fileid)

    job_queue.finish()



#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Project: 
 #  Filename: traverse_dir.py 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  3, 2015
 #  Time: 14:06:02
 #  Description: 
###############################################################################

from __future__ import print_function
import sys
import os
import re

import config_load

def traverse_dir(config):
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
            fileid = full_name[len(image_root_path) + 1:]
            #print(full_name, ":", fileid)

            job_queue.inqueue(0, full_name, fileid)

    job_queue.finish()



# command line arguments: lib_path conf_path
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: Command line arguments error. Please view source code to get help. ")
        exit(1)

    lib_path = str(sys.argv[1])
    conf_path = str(sys.argv[2])

    if not os.path.isabs(conf_path):
        print("Error: Configuration path", conf_path, "is not absolute path. ")
        exit(1)

    if not os.path.isabs(lib_path):
        print("Error: Library pth", lib_path, "is not absolute path. ")
        exit(1)

    # non-builtin modules mustn't be loaded before this statement
    sys.path.insert(0, lib_path)
    from job_queue import JobQueue

    # load config
    config = config_load.load_config(conf_path)

    print(config)

    traverse_dir(config)



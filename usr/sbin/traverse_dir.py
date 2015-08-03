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

sys.path.insert(0, "../lib/")

from job_queue import JobQueue


if __name__ == "__main__":

    # load config
    # TODO: test
    # config = load_config()
    config = { 
               "migrate.type": 2,
               "local.image_root_path": "~/Desktop/testdir",
               #"local.image_root_path": "../../../../Desktop/testdir",
               "appinfo.appid": "10000037",
               "appinfo.secretID": "AKIDpoKBfMK7aYcYNlqxnEtYA1ajAqji2P7T",
               "appinfo.secretKey": "P4FewbltIpGeAbwgdrG6eghMUVlpmjIe",
               "appinfo.bucket": "bucket",
               "Concurrency": 1
             }

    # check config
    mandatory_options = [ 
                          "migrate.type", 
                          "local.image_root_path", 
                          "appinfo.appid", 
                          "appinfo.secretID",
                          "appinfo.secretKey",
                          "appinfo.bucket"
                        ] 

    for option in mandatory_options:
        if option not in config:
            print("Error: Option", option, "is requiret. ")
            exit(1)
    
    # only filenames matching this regex will be uploaded, others would be ignored
    filename_pattern = re.compile(".*\.(?:jpg|jpeg|png|gif|bmp|webp)$", re.IGNORECASE)
    # use this to match all filenames
    # filename_pattern = None

    
    image_root_path = os.path.abspath(os.path.expanduser(config["local.image_root_path"]))

    job_queue = JobQueue(
                         config["Concurrency"],
                         config["appinfo.appid"],
                         config["appinfo.bucket"],
                         config["appinfo.secretID"],
                         config["appinfo.secretKey"]
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


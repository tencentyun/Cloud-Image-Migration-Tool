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
from multiprocessing import Queue
import re
import os
import random
import time


def traverse(config, log_path):
    from job_queue import JobQueue
    # check config
    mandatory_options = [ 
                          ("migrateinfo", "migrate.type"),
                          ("local", "local.image_root_path"), 
                          ("appinfo", "appinfo.appid"), 
                          ("appinfo", "appinfo.secretid"),
                          ("appinfo", "appinfo.secretkey"),
                          ("appinfo", "appinfo.bucket"),
                          ("toolconfig", "concurrency"),
                        ] 

    for section, option in mandatory_options:
        if section not in config or option not in config[section]:
            print("Error: Option", section + "." + option, "is required. ")
            exit(1)

    if not os.path.isabs(config["local"]["local.image_root_path"]):
        print("Error: Image root path", config["local"]["local.image_root_path"], "is not absolute path")
        exit(1)
    
    # only filenames matching this regex will be uploaded, others would be ignored
    filename_pattern = re.compile(".*\.(?:jpg|jpeg|png|gif|bmp|webp)$", re.IGNORECASE)
    # use this to match all filenames
    # filename_pattern = None

    
    image_root_path = os.path.abspath(os.path.expanduser(config["local"]["local.image_root_path"]))

    message_queue = Queue()
    
    num_processes = int(config["toolconfig"]["concurrency"])
    job_queue = JobQueue(
                         num_processes,
                         config["appinfo"]["appinfo.appid"],
                         config["appinfo"]["appinfo.bucket"],
                         config["appinfo"]["appinfo.secretid"],
                         config["appinfo"]["appinfo.secretkey"],
                         message_queue,
                        )
     
    # traverse dir
    for dirpath, dirs, files in os.walk(image_root_path):
        for filename in files:
            if filename_pattern and not filename_pattern.match(filename):
                continue
            full_name = os.path.join(dirpath, filename)
            fileid = full_name[len(image_root_path) + 1: ]
            # fileid = str(random.randrange(0, 999999999999999999)) + full_name[len(image_root_path) + 1: full_name.find(".")]
            # print(full_name, ":", fileid)

            job_queue.inqueue(0, full_name, fileid)
    
    # Queue is FIFO, so put finish flags after all jobs
    job_queue.inqueue_finish_flags()
     
    num_finished = 0
    with open(os.path.join(log_path, "stdout"), "w") as stdout, open(os.path.join(log_path, "stderr"), "w") as stderr:
        while True:
            message = message_queue.get()
            
            # success
            if message[0] == 0:
                stdout.write("%s: %s\n" % (time.asctime(), message))
            # failure
            elif message[0] == 1:
                stderr.write("%s: %s\n" % (time.asctime(), message))
            # job finish
            elif message[0] == 2:
                num_finished += 1
                stdout.write("%s: %d of %d processes finished \n" % (time.asctime(), num_finished, num_processes))
                if num_finished == num_processes:
                    break

        job_queue.finish()
        stdout.write("%s: master process finished \n" % time.asctime())



#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Project: 
 #  Filename: traverse_urllist.py 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  4, 2015
 #  Time: 12:28:25
 #  Description: 
###############################################################################

from multiprocessing import Queue

import os
import time
import random

def traverse(config, log_path):
    from job_queue import JobQueue
    import urlparse

    mandatory_options = [ 
                          ("migrateinfo", "migrate.type"),
                          ("urllist", "url.url_list_file_path"),
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

    if not os.path.isabs(config["urllist"]["url.url_list_file_path"]):
        print("Error: URL list file path", config["urllist"]["url.url_list_file_path"], "is not absolute path")
        exit(1)

    urllist_root_path = os.path.abspath(os.path.expanduser(config["urllist"]["url.url_list_file_path"]))

    message_queue = Queue()
    
    num_processes = int(config["toolconfig"]["concurrency"])
    job_queue = JobQueue(
                         int(config["toolconfig"]["concurrency"]),
                         config["appinfo"]["appinfo.appid"],
                         config["appinfo"]["appinfo.bucket"],
                         config["appinfo"]["appinfo.secretid"],
                         config["appinfo"]["appinfo.secretkey"],
                         message_queue,
                        )

    # treverse list
    with open(urllist_root_path) as f:
        for url in f:
            fileid = urlparse.urlparse(url).path
            if len(fileid) and fileid[0] == '/':
                # TODO: for now fileid cannot contains . /
                #fileid = fileid[1: ]
                fileid = str(random.randrange(0, 999999999999999999999999999999999999999999))
            #print(url)
            #print(fileid)
            job_queue.inqueue(2, url, fileid)

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



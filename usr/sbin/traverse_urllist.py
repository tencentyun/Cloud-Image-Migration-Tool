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

def traverse(config, log_path, job_queue):
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


    # treverse list
    with open(urllist_root_path) as f:
        for url in f:
            fileid = urlparse.urlparse(url).path
            if len(fileid) and fileid[0] == '/':
                fileid = fileid[1: ]
            job_queue.inqueue(2, url, fileid)




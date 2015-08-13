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
 #  Description: traverse a file consisting of URLs
###############################################################################

from __future__ import print_function
from multiprocessing import Queue

import os

def traverse(config, job_queue, skip):
    import urlparse

    mandatory_options = [ 
                          ("urllist", "url.url_list_file_path"),
                        ] 

    for section, option in mandatory_options:
        if section not in config or option not in config[section]:
            print("Error: Option", section + "." + option, "is required. ")
            exit(1)

    if not os.path.isabs(config["urllist"]["url.url_list_file_path"]):
        print("Error: URL list file path", config["urllist"]["url.url_list_file_path"], "is not absolute path. ")
        exit(1)

    if not os.path.isfile(config["urllist"]["url.url_list_file_path"]):
        print("Error: URL list file path", config["urllist"]["url.url_list_file_path"], "does not exist. ")
        exit(1)

    urllist_root_path = os.path.abspath(os.path.expanduser(config["urllist"]["url.url_list_file_path"]))

    # number of submited = totoal
    # number of skipped = already uploaded last time 
    num_submited = 0
    num_skipped = 0
    # treverse list
    with open(urllist_root_path) as f:
        for url in f:
            url = url.strip()
            if len(url) == 0: continue

            fileid = urlparse.urlparse(url).path
            if len(fileid) and fileid[0] == '/':
                fileid = fileid[1: ]

            num_submited += 1
            if fileid not in skip:
                job_queue.inqueue(2, url, fileid)
            else:
                num_skipped += 1

    return (num_submited, num_skipped)


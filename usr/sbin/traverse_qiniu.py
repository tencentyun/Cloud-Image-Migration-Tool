#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Project: 
 #  Filename: traverse_qiniu.py 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug 10, 2015
 #  Time: 14:56:39
 #  Description: traverse a qiniu bucket
###############################################################################

from __future__ import print_function
import re
import os
import sys
import urlparse
import urllib

# TODO: support non-ascii chars
def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def traverse(config, job_queue, skip):
    import qiniu

    # check config
    mandatory_options = [ 
                          ("qiniu", "qiniu.bucket"),
                          ("qiniu", "qiniu.accesskey"),
                          ("qiniu", "qiniu.secretkey"),
                          ("qiniu", "qiniu.domain"),
                          ("qiniu", "qiniu.start_offset"),
                          ("qiniu", "qiniu.total_num"),
                          ("qiniu", "qiniu.referer"),
                          ("qiniu", "qiniu.isprivate"),
                        ] 

    for section, option in mandatory_options:
        if section not in config or option not in config[section]:
            print("Error: Option", section + "." + option, "is required. ")
            exit(1)

    access_key = config["qiniu"]["qiniu.accesskey"]
    secret_key = config["qiniu"]["qiniu.secretkey"]
    bucket_name = config["qiniu"]["qiniu.bucket"]
    domain = config["qiniu"]["qiniu.domain"]
    offset = config["qiniu"]["qiniu.start_offset"]
    offset = int(offset) if len(offset) else 0
    num = config["qiniu"]["qiniu.total_num"]
    num = int(num) if len(num) else sys.maxint
    referer = config["qiniu"]["qiniu.referer"]
    referer = referer if len(referer) else None
    is_private = config["qiniu"]["qiniu.isprivate"]
    is_private = True if is_private == "1" or is_private.lower() == "true" else False



    # number of submited = totoal
    # number of skipped = already uploaded last time 
    num_submited = 0
    num_skipped = 0

    if True:
        qn = qiniu.Auth(access_key, secret_key) 
        bucket = qiniu.BucketManager(qn)

        count = 0
        marker = None
        eof = False
        while eof is False:
            ret, eof, info = bucket.list(bucket_name, prefix = None, marker = marker, limit = None)
            marker = ret.get("marker", None)

            # skip
            if count + len(ret["items"]) < offset:
                count += len(ret["items"])
                continue

            for item in ret["items"]:
                if count >= offset and count < offset + num:
                    fileid = item["key"].encode("utf-8")
                    
                    #url = urlparse.urljoin(domain, urllib.quote(fileid))
                    url = urlparse.urljoin(domain, fileid)
                    
                    if is_private:
                        url = qn.private_download_url(url, expires = 3600 * 24 * 365)

                    if fileid not in skip:
                        if referer:
                            job_queue.inqueue(3, (url, referer), fileid)
                        else:
                            job_queue.inqueue(2, url, fileid)
                    else:
                        num_skipped += 1
                    num_submited += 1
                count += 1
        if eof is not True:
            # error
            pass

    return (num_submited, num_skipped)
    

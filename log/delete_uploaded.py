#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: 
 #  Filename: delete_uploaded.py 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  5, 2015
 #  Time: 12:45:42
 #  Description: 
###############################################################################

from __future__ import print_function
from multiprocessing import Pool
import re
import sys
sys.path.insert(0, "../usr/lib/")
import tencentyun

appid = '10000037'
secret_id = 'AKIDpoKBfMK7aYcYNlqxnEtYA1ajAqji2P7T'
secret_key = 'P4FewbltIpGeAbwgdrG6eghMUVlpmjIe'

bucket = 'test0706'

image_obj = tencentyun.ImageV2(appid,secret_id,secret_key)

fileid_list = []

def extract_fileid(f):
    for line in f:
        match_result = re.match("^.*file id == ([^,]+),.*$", line)
        if match_result and len(match_result.groups()):
            fileid = match_result.groups()[0]
            fileid_list.append(fileid)
            #image_obj.delete(bucket, fileid)

def do_delete(fileid):
    image_obj.delete(bucket, fileid) 

with open("stderr") as f1, open("stdout") as f2:
    extract_fileid(f1)
    extract_fileid(f2)

print("%d file ids" % len(fileid_list))

pool = Pool(10)
pool.map(do_delete, fileid_list)


#!/usr/bin/env python

import sys
sys.path.insert(0, "../lib/")

import tencentyun

appid = "10000037"
secret_id = "AKIDpoKBfMK7aYcYNlqxnEtYA1ajAqji2P7T"
secret_key = "P4FewbltIpGeAbwgdrG6eghMUVlpmjIe"
bucket = "bucket"

fileids = [ "111.jpeg", 
            "download.jpeg", 
            "images.jpeg", 
            "tree-247122.jpg", 
            "dir1/images.jpeg", 
            "dir1/subdir/UK_Creative_462809583.jpg", 
            "dir1/subdir/images.jpeg", 
            "dir1/subdir/tree-247122.jpg", 
            "dir1/asdas2121sa--++:as123:.jpeg",
            "ok.jpeg"
          ]
image_obj = tencentyun.ImageV2(appid, secret_id, secret_key)

for fileid in fileids:
    image_obj.delete(bucket, fileid)

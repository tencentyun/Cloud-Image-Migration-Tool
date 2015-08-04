#!/usr/bin/env python

import sys
sys.path.insert(0, "../lib/")

import tencentyun

#appid = "10000037"
#secret_id = "AKIDpoKBfMK7aYcYNlqxnEtYA1ajAqji2P7T"
#secret_key = "P4FewbltIpGeAbwgdrG6eghMUVlpmjIe"
#bucket = "bucket"

#appid = "10000002"
#secret_id = "AKIDL5iZVplWMenB5Zrx47X78mnCM3F5xDbC"
#secret_key = "Lraz7n2vNcyW3tiP646xYdfr5KBV4YAv"
#bucket = "test1"


appid = "10001818"
secret_id = "AKID1Q25kCKsgs5ZTlGsdzXi0z394LptiQQS"
secret_key = "tQSzSEj6hvc1e43X5ejExIuG9lihGcdR"
bucket = "tencentyun"



fileids = [ 

"1.jpeg",
"2.jpeg",
"3.jpeg",
"4411111.jpg",
"68asidjui.jpg",
"8099.jpeg",

"1",
"2",
"3",
"4411111",
"68asidjui",
"8099"


          ]
image_obj = tencentyun.ImageV2(appid, secret_id, secret_key)

for fileid in fileids:
    image_obj.delete(bucket, fileid)

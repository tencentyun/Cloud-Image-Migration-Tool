#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Project: 
 #  Filename: uploader.py 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  3, 2015
 #  Time: 13:29:39
 #  Description: 
###############################################################################


from __future__ import print_function
import tencentyun

class Uploader(object):
    def __init__(self, appid, bucket, secret_id, secret_key):
        self.appid = appid
        self.bucket = bucket
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.image_obj = tencentyun.ImageV2(self.appid, self.secret_id, self.secret_key)

    # return (0, info) on success
    # return (1, info) on failure
    def upload_filename(self, filename, fileid):
        response_obj = self.image_obj.upload(filename, self.bucket, fileid)
        
        if "code" in response_obj and response_obj["code"] == 0:
            return (0, "file id == " + fileid + ", download URL == " + response_obj["data"]["download_url"])
        else:
            return (1, "file id == " + fileid + ", response packet == " + str(response_obj))
        

    def upload_binary(self, binary, fileid):
        response_obj = self.image_obj.upload_binary(binary, self.bucket, fileid)

        if "code" in response_obj and response_obj["code"] == 0:
            return (0, "file id == " + fileid + ", download URL == " + response_obj["data"]["download_url"])
        else:
            return (1, "file id == " + fileid + ", response packet == " + str(response_obj))
        

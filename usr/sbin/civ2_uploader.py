#!/usr/bin/env python

from base_uploader import BaseUploader

import tencentyun

class CloudImageV2Uploader(BaseUploader):
    mandatory_options = [
        ("appinfo", "appinfo.appid"),
        ("appinfo", "appinfo.bucket"),
        ("appinfo", "appinfo.secretid"),
        ("appinfo", "appinfo.secretkey"),
                        ]

    def __init__(self, config):
        super(CloudImageV2Uploader, self).__init__(config)
        self.appid = config["appinfo"]["appinfo.appid"]
        self.bucket = config["appinfo"]["appinfo.bucket"]
        self.secret_ID = config["appinfo"]["appinfo.secretid"]
        self.secret_key = config["appinfo"]["appinfo.secretkey"]
        self.image_obj = tencentyun.ImageV2(self.appid, self.secret_ID, self.secret_key)
    
    @staticmethod
    def check_config(config):
        for section, option in CloudImageV2Uploader.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

    # implementation of abstract method
    def upload(self, job):
        """
        type job: (fileid, source)
        rtype: (new fileid, status, log)

        do not throw any exception
        """
        fileid = job[0]
        source = job[1]

        new_fileid = fileid
        status = None
        log = None


        try:
            response_obj = self.image_obj.upload_binary(source, self.bucket, fileid)

            if "code" in response_obj and response_obj["code"] == 0:
                status = 1
                log = None
            else:
                status = 2
                log = []
                if "message" in response_obj:
                    log.append("message: %s" % response_obj["message"].encode("utf-8"))
                if "code" in response_obj:
                    log.append("code: %d" % response_obj["code"])
                if "httpcode" in response_obj:
                    log.append("httpcode: %d" % response_obj["httpcode"])
            if log:
                log = ", ".join(log)
        except Exception as e:
            if not status:
                status = 2
            if not log:
                log = str(e)

        return (new_fileid, status, log)

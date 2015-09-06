#!/usr/bin/env python

from base_job_manager import BaseJobManager

import os
import urlparse
import qiniu

class QiniuJobManager(BaseJobManager):
    mandatory_options = [
        ("qiniu", "qiniu.accesskey"),
        ("qiniu", "qiniu.secretkey"),
        ("qiniu", "qiniu.bucket"),
        ("qiniu", "qiniu.domain"),
        ("qiniu", "qiniu.isprivate"),
                        ]

    @staticmethod
    def check_config(config):
        for section, option in QiniuJobManager.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        if config["qiniu"]["qiniu.isprivate"].lower() not in [ "true", "false", "0", "1", "t", "f", "yes", "no", "y", "n" ]:
            return "Error: Invalid Qiniu.qiniu.isprivate. "

    def do(self):
        access_key = self.config["qiniu"]["qiniu.accesskey"]
        secret_key = self.config["qiniu"]["qiniu.secretkey"]
        bucket_name = self.config["qiniu"]["qiniu.bucket"]
        domain = self.config["qiniu"]["qiniu.domain"]
        is_private = self.config["qiniu"]["qiniu.isprivate"].lower() in [ "true", "1", "t", "yes", "y" ]
        if "qiniu" in self.config and "qiniu.referer" in self.config["qiniu"]:
            referer = self.config["qiniu"]["qiniu.referer"]
        else:
            referer = None

        qn = qiniu.Auth(access_key, secret_key)
        bucket = qiniu.BucketManager(qn)

        marker = None
        eof = False
        while eof is False:
            (ret, eof, info) = bucket.list(bucket_name, prefix = None, marker = marker, limit = None)
            marker = ret.get("marker", None)
            for item in ret["items"]:
                fileid = item["key"].encode("utf-8")
                url = urlparse.urljoin(domain, fileid)

                if is_private:
                    url = qn.private_download_url(url, expires = 3600 * 24 * 365)

                if referer:
                    self.submit(fileid, url + "\t" + referer)
                else:
                    self.submit(fileid, url)
        if eof is not True:
            # error
            pass

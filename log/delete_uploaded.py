#!/usr/bin/env python

from __future__ import print_function
from multiprocessing import Pool
import re
import sys
import sqlite3
sys.path.insert(0, "../usr/lib/")
import tencentyun

appid = "10000214"
secret_id = "AKIDXtyLtUwFsCThwJ8wR4QFiJXLKCU7aEHr"
secret_key = "ce4thuWI1Ib2LlDqcI5gmIEfnJPi1NCs"
bucket = "newbucket"

image_obj = tencentyun.ImageV2(appid,secret_id,secret_key)

fileid_list = []

def extract_fileid(db_file):
    conn = sqlite3.connect(db_file)
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute("SELECT fileid from jobs")
    for row in cur:
        fileid_list.append(row[0])

def do_delete(fileid):
    try:
        print(image_obj.delete(bucket, fileid)["message"])
    except Exception as e:
        print(e)

pool = Pool(10)

extract_fileid("jobs.db")

print("%d file ids" % len(fileid_list))

pool.map(do_delete, fileid_list)


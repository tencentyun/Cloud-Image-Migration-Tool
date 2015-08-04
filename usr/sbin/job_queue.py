#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Project: 
 #  Filename: job_queue.py 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  3, 2015
 #  Time: 13:49:09
 #  Description: 
###############################################################################

from __future__ import print_function
from multiprocessing import Process, Queue
import requests
import urllib

from uploader import Uploader

class JobQueue(object):
    # number of uploaders
    def __init__(self, num_uploaders, appid, bucket, secret_id, secret_key):
        self.queue = Queue()
        self.slave_processes = []
        for i in range(num_uploaders):
            slave = Uploader(appid, bucket, secret_id, secret_key)
            
            slave_process = Process(target = self.dequeue, args = (i, slave, ))
            slave_process.daemon = True
            slave_process.start()

            self.slave_processes.append(slave_process)

    # push a job into queue
    # job type: 0 -- filename on disk, 
    #           1 -- binary data in memory 
    #           2 -- url
    def inqueue(self, job_type, job_obj, job_fileid):
        self.queue.put((job_type, job_obj, job_fileid))
        # print("inqueue:", job_fileid)
    
    def kill(self):
        # clear job queue
        while not self.queue.empty():
            self.queue.get()
        # wait finish
        self.finish()
        
    def finish(self):
        # TODO: handle when child processes is killed
        while not self.queue.empty():
            pass

        for _ in range(len(self.slave_processes)):
            self.queue.put("Finished")

        for process in self.slave_processes:
            process.join()

    def dequeue(self, process_id, slave):
        while True:
            job = self.queue.get()
            
            if job == "Finished":
                break
            
            # print(process_id, "get job: ", job)
            if job[0] == 0:
                return_obj = slave.upload_filename(job[1], job[2])
            elif job[0] == 1:
                return_obj = slave.upload_binary(job[1], job[2])
            elif job[0] == 2:
                bin_image = urllib.urlopen(job[1]).read()
                #with open("/Users/jamis/Desktop/url/" + job[2].replace("/", "%2f"), "wb") as f:
                #    f.write(bin_image)
                return_obj = slave.upload_binary(bin_image, job[2])
            # TODO: handle error
    

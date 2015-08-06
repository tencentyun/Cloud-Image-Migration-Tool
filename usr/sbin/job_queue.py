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
 #  Description: a queue to manage jobs and slave workers
###############################################################################

from __future__ import print_function
import Queue
import multiprocessing
import requests
import urllib
import signal
import os

# debug
import logging
mpl = multiprocessing.log_to_stderr()
mpl.setLevel(logging.INFO)

from uploader import Uploader

class JobQueue(object):
    # number of uploaders
    def __init__(self, num_uploaders, appid, bucket, secret_id, secret_key, message_queue, pid_log):
        self.ready_queue = []
        self.ready_queue_index = 0
        self.queue = multiprocessing.Queue(200)
        self.slave_processes = []
        pid_log_lock = multiprocessing.Lock()
        for i in range(num_uploaders):
            slave = Uploader(appid, bucket, secret_id, secret_key)
            
            slave_process = multiprocessing.Process(
                target = self.dequeue, 
                args = (i, slave, message_queue, pid_log, pid_log_lock ))
            slave_process.daemon = True
            slave_process.start()

            self.slave_processes.append(slave_process)

    # push a job into queue
    # job type: 0 -- filename on disk, 
    #           1 -- binary data in memory 
    #           2 -- url
    def inqueue(self, job_type, job_obj, job_fileid):
        self.ready_queue.append((job_type, job_obj, job_fileid))

    # this function must be called when queue is empty
    def fill_queue(self):
        while self.ready_queue_index < len(self.ready_queue):
            try:
                self.queue.put_nowait(self.ready_queue[self.ready_queue_index])
                self.ready_queue_index += 1
                fill_count += 1
            except Queue.Full:
                break

    def inqueue_finish_flags(self):
        for _ in range(len(self.slave_processes)):
            self.ready_queue.append("Finished")
    
    # delete all jobs already submited, wait until all subprocesses quit
    def stop(self):
        # clear queue
        while True:
            try:
                self.queue.get_nowait()
            except Queue.Empty:
                break
        
        # ignore jobs in ready_queue
        self.ready_queue_index = len(self.ready_queue)
        self.inqueue_finish_flags()
        self.fill_queue()
        self.finish()

    # block until all child processes end
    def finish(self):
        for process in self.slave_processes:
            process.join()

    def dequeue(self, process_id, slave, message_queue, pid_log, pid_log_lock):
        with pid_log_lock:
            pid_log(os.getpid())

        def ignore(signal, frame):
            pass

        signal.signal(signal.SIGINT, ignore)

        while True:
            job = self.queue.get()
            
            if job == "Finished":
                # insert finish message to message queue
                message_queue.put((2,))
                break
            
            try:
                if job[0] == 0:
                    return_obj = slave.upload_filename(job[1], job[2])
                elif job[0] == 1:
                    return_obj = slave.upload_binary(job[1], job[2])
                elif job[0] == 2:
                    bin_image = urllib.urlopen(job[1]).read()
                    #with open("/Users/jamis/Desktop/url/" + job[2].replace("/", "%2f"), "wb") as f:
                    #    f.write(bin_image)
                    return_obj = slave.upload_binary(bin_image, job[2])
                message_queue.put(return_obj)
            except Exception as e:
                message_queue.put((1, "file id == " + job[2] + ", exception: " + str(e)))
            

    

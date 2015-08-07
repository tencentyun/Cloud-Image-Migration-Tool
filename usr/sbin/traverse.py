#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Project: 
 #  Filename: traverse.py 
 #  Version: 1.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Aug  3, 2015
 #  Time: 14:06:02
 #  Description: call different traverse functions to load jobs
 #               manage status of jobs 
 #               log
###############################################################################

from __future__ import print_function
import sys
import os
import re
import multiprocessing
import time
import Queue

import config_load
import traverse_dir 
import traverse_urllist 


# command line arguments: lib_path conf_path log path
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Error: Command line arguments error. Please view source code to get help. ")
        exit(1)

    lib_path = str(sys.argv[1])
    conf_path = str(sys.argv[2])
    log_path = str(sys.argv[3])

    if not os.path.isabs(conf_path):
        print("Error: Configuration path", conf_path, "is not absolute path. ")
        exit(1)

    if not os.path.isabs(lib_path):
        print("Error: Library pth", lib_path, "is not absolute path. ")
        exit(1)

    if not os.path.isabs(log_path):
        print("Error: Log path", log_path, "is not absolute path. ")
        exit(1)

    if not os.path.exists(log_path):
        os.mkdir(log_path)

    if not os.path.isdir(log_path):
        print("Error: Log path", log_path, "is not directory or not exists. ")
        exit(1)
    

    skip = set()
    if os.path.exists(os.path.join(log_path, "stdout")):
        with open(os.path.join(log_path, "stdout")) as accomplished:
            for line in accomplished:
                match_result = re.match("^.*file id == ([^,\n]+),?.*$", line)
                if match_result and len(match_result.groups()):
                    fileid = match_result.groups()[0]
                    skip.add(fileid)



    # non-builtin modules mustn't be loaded before this statement
    sys.path.insert(0, lib_path)
    from job_queue import JobQueue

    # load config
    config = config_load.load_config(conf_path)

    # print(config)

    mandatory_options = [ 
                          ("migrateinfo", "migrate.type"),
                          ("appinfo", "appinfo.appid"), 
                          ("appinfo", "appinfo.secretid"),
                          ("appinfo", "appinfo.secretkey"),
                          ("appinfo", "appinfo.bucket"),
                          ("toolconfig", "concurrency"),
                        ] 

    for section, option in mandatory_options:
        if section not in config or option not in config[section]:
            print("Error: Option", section + "." + option, "is required. ")
            exit(1)

    if not config["toolconfig"]["concurrency"].isdigit() or int(config["toolconfig"]["concurrency"]) <= 0:
        print("Error: Minimum of toolconfig.cocurrency is 1. ")
        exit(1)



    traverse_functions = [ 
                           traverse_dir.traverse,
                           traverse_urllist.traverse,
                           # other traverse methods
                         ]

    with open(os.path.join(log_path, "pid"), "w") as f:
        f.write(str(os.getpid()) + "\n") 

    # start parallel uploading
    try:
        message_queue = multiprocessing.Queue()
        
        num_processes = int(config["toolconfig"]["concurrency"])
        
        pid_file = open(os.path.join(log_path, "pid"), "a");

        # Note that pids of child processes must be flushed to on-disk file immediately it starts
        # or there's a risk of resouce leak
        def write_pid_log(pid):
            pid_file.write(str(pid) + "\n")
            pid_file.flush()
            

        job_queue = JobQueue(
                             num_processes,
                             config["appinfo"]["appinfo.appid"],
                             config["appinfo"]["appinfo.bucket"],
                             config["appinfo"]["appinfo.secretid"],
                             config["appinfo"]["appinfo.secretkey"],
                             message_queue,
                             write_pid_log,
                            )
        
        pid_file.close()
         
        # traverse dir OR traver urllist OR other methods
        num_submited, num_skipped = \
            traverse_functions[int(config["migrateinfo"]["migrate.type"]) - 1](config, log_path, job_queue, skip)
        num_failed, num_successful = 0, num_skipped

        # Queue is FIFO, so put finish flags after all jobs
        job_queue.inqueue_finish_flags()
         
        num_finished = 0

        # if proceed unfinished jobs, stdout will be appeneded, stderr will be overwritten
        stdout = open(os.path.join(log_path, "stdout"), "a")
        stderr = open(os.path.join(log_path, "stderr"), "w")
        state_flush_time = 0
        state_flush_interval = 0.5
        state = open(os.path.join(log_path, "state"), "w")

        # receive message from child processes, write to log
        while True:
            job_queue.fill_queue()
            message = message_queue.get()
            
            # success
            if message[0] == 0:
                stdout.write("%s: %s\n" % (time.asctime(), message[1]))
                num_successful += 1
            # failure
            elif message[0] == 1:
                stderr.write("%s: %s\n" % (time.asctime(), message[1]))
                num_failed += 1
            # job finish
            elif message[0] == 2:
                num_finished += 1
                stdout.write("%s: %d of %d processes finished \n" % (time.asctime(), num_finished, num_processes))
                if num_finished == num_processes:
                    state.write("failed, successful / submited: %d, %d / %d\n" % (num_failed, num_successful, num_submited))
                    state.flush()
                    break

            if time.time() - state_flush_time > state_flush_interval:
                state.write("failed, successful / submited: %d, %d / %d\n" % (num_failed, num_successful, num_submited))
                state.flush()
                state_flush_time = time.time()

        job_queue.finish()
        stdout.write("%s: master process finished \n" % time.asctime())
    except KeyboardInterrupt:
        if "job_queue" in locals():
            job_queue.stop()


            while True:
                try:
                    message = message_queue.get_nowait()
                    
                    # success
                    if message[0] == 0 and "stdout" in locals():
                        stdout.write("%s: %s\n" % (time.asctime(), message[1]))
                        num_successful += 1
                    # failure
                    elif message[0] == 1 and "stderr" in locals():
                        stderr.write("%s: %s\n" % (time.asctime(), message[1]))
                        num_failed += 1
                    # job finish
                    elif message[0] == 2 and "stdout" in locals():
                        num_finished += 1
                        stdout.write("%s: %d of %d processes interrupted \n" % (time.asctime(), num_finished, num_processes))
                    
                    if "state" in locals() and time.time() - state_flush_time > state_flush_interval:
                        state.write("failed, successful / submited: %d, %d / %d\n" % (num_failed, num_successful, num_submited))
                        state.flush()
                        state_flush_time = time.time()

                except Queue.Empty:
                    if "state" in locals():
                        state.write("failed, successful / submited: %d, %d / %d\n" % (num_failed, num_successful, num_submited))
                        state.flush()
                    break
            if "stdout" in locals():
                stdout.write("%s: master process interrupted \n" % time.asctime())
    finally:
        if "pid_file" in locals():
            pid_file.close()
        if "stdout" in locals():
            stdout.close()
        if "stderr" in locals():
            stderr.close()
        if "state" in locals():
            state.close()



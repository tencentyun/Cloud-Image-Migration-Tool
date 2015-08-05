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
 #  Description: 
###############################################################################

from __future__ import print_function
import sys
import os
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
    
    log_files = [ "stdout", "stderr", ]
    log_files = [ os.path.join(log_path, x) for x in log_files ] 

    for log_file in log_files:
        if os.path.exists(log_file):
            print("Error:", log_file, "alreadty exists. ")
            exit(1)



    # non-builtin modules mustn't be loaded before this statement
    sys.path.insert(0, lib_path)
    from job_queue import JobQueue

    # load config
    config = config_load.load_config(conf_path)

    # print(config)

    migrate_type = ("migrateinfo", "migrate.type")

    if migrate_type[0] not in config or migrate_type[1] not in config[migrate_type[0]]:
        print("Error: Option", migrate_type[0] + "." + migrate_type[1], "is required. ")

    traverse_functions = [ 
                           traverse_dir.traverse,
                           traverse_urllist.traverse,
                           # other traverse methods
                         ]

    #traverse_functions[int(config[migrate_type[0]][migrate_type[1]]) - 1](config, log_path)


    # start parallel uploading
    try:
        message_queue = multiprocessing.Queue()
        
        num_processes = int(config["toolconfig"]["concurrency"])
        job_queue = JobQueue(
                             num_processes,
                             config["appinfo"]["appinfo.appid"],
                             config["appinfo"]["appinfo.bucket"],
                             config["appinfo"]["appinfo.secretid"],
                             config["appinfo"]["appinfo.secretkey"],
                             message_queue,
                            )
         
        # traverse dir OR traver urllist OR other methods
        traverse_functions[int(config[migrate_type[0]][migrate_type[1]]) - 1](config, log_path, job_queue)

        # Queue is FIFO, so put finish flags after all jobs
        job_queue.inqueue_finish_flags()
         
        num_finished = 0

        stdout = open(os.path.join(log_path, "stdout"), "w")
        stderr = open(os.path.join(log_path, "stderr"), "w")
        # receive message from child processes, write to log
        while True:
            message = message_queue.get()
            
            # success
            if message[0] == 0:
                stdout.write("%s: %s\n" % (time.asctime(), message))
            # failure
            elif message[0] == 1:
                stderr.write("%s: %s\n" % (time.asctime(), message))
            # job finish
            elif message[0] == 2:
                num_finished += 1
                stdout.write("%s: %d of %d processes finished \n" % (time.asctime(), num_finished, num_processes))
                if num_finished == num_processes:
                    break

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
                        stdout.write("%s: %s\n" % (time.asctime(), message))
                    # failure
                    elif message[0] == 1 and "stderr" in locals():
                        stderr.write("%s: %s\n" % (time.asctime(), message))
                    # job finish
                    elif message[0] == 2 and "stdout" in locals():
                        num_finished += 1
                        stdout.write("%s: %d of %d processes interrupted \n" % (time.asctime(), num_finished, num_processes))
                except Queue.Empty:
                    break
            if "stdout" in locals():
                stdout.write("%s: master process interrupted \n" % time.asctime())
    finally:
        if "stdout" in locals():
            stdout.close()
        if "stderr" in locals():
            stderr.close()



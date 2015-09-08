#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Tencent Inc.
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: Cloud Image Migration Tool
 #  Filename: main.py
 #  Version: 2.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Sep  7, 2015
 #  Time: 14:29:44
###############################################################################
"""
This module is called by shell script.
In this module, we check command-line arguments, load configurations and check 
configurations. Then job manager module or master module is called according to
the configuration to submit jobs or upload jobs.
"""

from __future__ import print_function
import os
import sys

from config_loader import ConfigLoader
from master import Master
from base_job_manager import BaseJobManager
from local_fs_job_manager import LocalFSJobManager
from url_list_job_manager import URLListJobManager
from base_slave import BaseSlave
from url_slave import URLSlave
from base_uploader import BaseUploader


def import_libs():
    """
    Import non-builtin modules or modules contain non-builtin modules.

    Args: None
        
    Returns: Returns nothing
    """
    global CloudImageV2Uploader  
    from civ2_uploader import CloudImageV2Uploader
    global QiniuJobManager
    from qiniu_job_manager import QiniuJobManager

def check_args(argv):
    """
    Check command-line arguments passed to this module.
    
    Args:
        argv: A list of command-line arguments
    
    Returns:
        Returns a string containing error message if there are errors in 
        command-line arguments.

        Otherwise returns a tuple consisting of three strings and an integer.
            (lib_path, conf_path, log_path, task)
            lib_path: Absolute path of modules integrated in this tool
            conf_path: Absolute path of configuration file
            log_path: Absolute path of log
            task: integer 0 if submitting jobs, 1 if uploading jobs
    """
    if len(sys.argv) < 5:
        return "Error: Command line arguments error. Please view source code for help. "
    
    lib_path = str(argv[1])
    conf_path = str(argv[2])
    log_path = str(argv[3])
    task = str(argv[4])

    if not os.path.isabs(conf_path):
        return "Error: Configuration path %s is not absolute path. " % conf_path

    if not os.path.isfile(conf_path):
        return "Error: Configuration path %s is not regular file. " % conf_path

    if not os.path.isabs(lib_path):
        return "Error: Library path %s is not absolute path. " % lib_path

    if not os.path.isabs(log_path):
        return "Error: Log path %s is not absolute path. " % log_path

    if not os.path.exists(log_path):
        os.mkdir(log_path)

    if not os.path.isdir(log_path):
        return "Error: Log path %s is not directory or not exists. " % log_path

    if task != "submit" and task != "upload":
        return "Error: Invalid task. "

    task = { "submit": 0,
             "upload": 1,
           }[task]


    return (lib_path, conf_path, log_path, task)

def check_config(config):
    """
    Check configurations in config.ini.

    Args:
        config: A dict whose key is section name of config file, and value is 
            another dict. The secondary dict's key is property name and value is
            property value.

    Returns:
        Returns a string containing error message if there are errors in
        configuration.

        Otherwise returns a tuple consisting of three derived class.
            (job_manager_class, slave_class, uploader_class)
            job_manager_class: Derived class of BaseJobManager. It determines 
                file id and source of jobs.
            slave_class: Derived class of BaseSlave. It retrieves resources 
                according to the source and sends it to uploader_class.
            uploader_class: Derived class of BaseUploader, which will upload 
                resources to somewhere.
    """

    import_libs()

    derived_classes = { 
        "Local": (LocalFSJobManager, URLSlave, CloudImageV2Uploader),
        "URLList": (URLListJobManager, URLSlave, CloudImageV2Uploader),
        "Qiniu": (QiniuJobManager, URLSlave, CloudImageV2Uploader),
                      }

    # check config for base job manager
    check_result = BaseJobManager.check_config(config)
    if check_result:
        return check_result

    # check config for base slave
    check_result = BaseSlave.check_config(config)
    if check_result:
        return check_result

    # check config for base uploader
    check_result  = BaseUploader.check_config(config)
    if check_result:
        return check_reuslt
    
    class_type = config["migrateinfo"]["migrate.type"]
    job_manager_class = derived_classes[class_type][0]
    slave_class = derived_classes[class_type][1]
    uploader_class = derived_classes[class_type][2]

    # check config for derived job manager and slave and uploader
    check_result = job_manager_class.check_config(config)
    if check_result:
        return check_result

    check_result = slave_class.check_config(config)
    if check_result:
        return check_result

    check_result = uploader_class.check_config(config)
    if check_result:
        return check_result

    # check config for master
    check_result = Master.check_config(config)
    if check_result:
        return check_result

    
    return (job_manager_class, slave_class, uploader_class)

# command line arguments: lib_path conf_path log_path task
if __name__ == "__main__":
    """ 
    This is main function.
    It writes pid log and call job manager to start submitting jobs, 
    or call uploader to start uploading.
    """

    # check command line arguments
    check_result = check_args(sys.argv)
    if type(check_result) is str:
        print(check_result)
        exit(1)
    else:
        (lib_path, conf_path, log_path, task) = check_result

    # non-builtin modules mustn't be imported before this statement
    sys.path.insert(0, lib_path)

    # load configurations
    config = ConfigLoader.load(conf_path)
    config["paths"] = dict()
    config["paths"]["lib_path"] = lib_path
    config["paths"]["conf_path"] = conf_path
    config["paths"]["log_path"] = log_path
    config["paths"]["job_db_path"] = os.path.join(log_path, "jobs.db")
    config["paths"]["pid_path"] = os.path.join(log_path, "pid")

    # check configurations
    check_result = check_config(config)
    if type(check_result) is str:
        print(check_result)
        exit(1)
    else:
        (job_manager_class, slave_class, uploader_class) = check_result

    pid_path = config["paths"]["pid_path"]
    with open(pid_path, "w") as pid:
        pid.write(str(os.getpid()))

    if task == 0:
        # submit procedure
        job_manager = job_manager_class(config)
        job_manager.start()
        print("New submitted: %d" % job_manager.new_submitted)
        print("Submit failed: %d" % job_manager.submit_error)
        print("Ignored: %d" % job_manager.ignore)
    elif task == 1: 
        # upload procedure
        master = Master(config, slave_class, uploader_class)
        master.start()

    if os.path.isfile(pid_path):
        os.remove(pid_path)

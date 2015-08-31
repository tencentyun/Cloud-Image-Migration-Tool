#!/usr/bin/env python

from __future__ import print_function
import os
import sys

from config_loader import ConfigLoader
from base_job_manager import BaseJobManager
from local_fs_job_manager import LocalFSJobManager
from url_slave import URLSlave
from master import Master

def check_args(argv):
    if len(sys.argv) < 4:
        return "Error: Command line arguments error. Please view source code for help. "
    
    lib_path = str(argv[1])
    conf_path = str(argv[2])
    log_path = str(argv[3])

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


    return (lib_path, conf_path, log_path)

def check_config(config):
    derived_classes = { 
        "1": (LocalFSJobManager, URLSlave),
                       }

    # check config for base job manager
    check_result = BaseJobManager.check_config(config)
    if check_result:
        return check_result

    # check config for base slave
    check_result = BaseSlave.check_config(config)
    if check_result:
        return check_result
    
    job_manager_class = derived_classes[config["migrateinfo"]["migrate.type"]][0]
    slave_class = derived_classes[config["migrateinfo"]["migrate.type"]][1]

    # check config for derived job manager and slave
    check_result = job_manager_class.check_config(config)
    if check_result:
        return check_result

    check_result = slave_class.check_config(config)
    if check_result:
        return check_result

    # check config for master
    check_result = Master.check_config(config)
    if check_result:
        return check_result
    
    return (job_manager_class, slave_class)

# command line arguments: lib_path conf_path log_path
if __name__ == "__main__":

    # check command line arguments
    check_result = check_args(sys.argv)
    if type(check_result) is str:
        print(check_result)
        exit(1)
    else:
        (lib_path, conf_path, log_path) = check_result

    # non-builtin modules mustn't be imported before statement
    sys.path.insert(0, lib_path)

    # load configurations
    config = ConfigLoader.load(conf_path)
    config["paths"] = dict()
    config["paths"]["lib_path"] = lib_path
    config["paths"]["conf_path"] = conf_path
    config["paths"]["log_path"] = log_path
    config["paths"]["job_db_path"] = os.path.join(log_path, "jobs.db")

    # check configurations
    check_result = check_config(config)
    if type(check_result) is str:
        print(check_result)
        exit(1)
    else:
        (job_manager_class, slave_class) = check_result

    # submit procedure
    job_manager = job_manager_class(config)
    #job_manager.do()
    
    #print("New submitted: %d" % job_manager.new_submitted)
    #print("Submit failed: %d" % job_manager.submit_error)
    
    # upload procedure
    master = Master(config, slave_class)
    master.start()

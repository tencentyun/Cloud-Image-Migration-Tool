#!/usr/bin/env python

from __future__ import print_function
import os
import sys

from config_loader import ConfigLoader
from master import Master
from base_job_manager import BaseJobManager
from local_fs_job_manager import LocalFSJobManager
from base_slave import BaseSlave
from url_slave import URLSlave
from base_uploader import BaseUploader


# import non-builtin modules or modules contain non-builtin modules here
def import_libs():
    global CloudImageV2Uploader  
    from civ2_uploader import CloudImageV2Uploader

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
    import_libs()

    derived_classes = { 
        "1": (LocalFSJobManager, URLSlave, CloudImageV2Uploader),
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

# command line arguments: lib_path conf_path log_path
if __name__ == "__main__":

    # check command line arguments
    check_result = check_args(sys.argv)
    if type(check_result) is str:
        print(check_result)
        exit(1)
    else:
        (lib_path, conf_path, log_path) = check_result

    # non-builtin modules mustn't be imported before this statement
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
        (job_manager_class, slave_class, uploader_class) = check_result

    # submit procedure
    #job_manager = job_manager_class(config)
    #job_manager.do()
    #print("New submitted: %d" % job_manager.new_submitted)
    #print("Submit failed: %d" % job_manager.submit_error)
    #print("Ignored: %d" % job_manager.ignore)
    
    # upload procedure
    master = Master(config, slave_class, uploader_class)
    master.start()

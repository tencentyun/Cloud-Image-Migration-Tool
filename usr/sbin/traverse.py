#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Jamis Hoo
 #  Project: 
 #  Filename: traverse_dir.py 
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

import config_load
import traverse_dir 
import traverse_urllist 



# command line arguments: lib_path conf_path
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: Command line arguments error. Please view source code to get help. ")
        exit(1)

    lib_path = str(sys.argv[1])
    conf_path = str(sys.argv[2])

    if not os.path.isabs(conf_path):
        print("Error: Configuration path", conf_path, "is not absolute path. ")
        exit(1)

    if not os.path.isabs(lib_path):
        print("Error: Library pth", lib_path, "is not absolute path. ")
        exit(1)

    # non-builtin modules mustn't be loaded before this statement
    sys.path.insert(0, lib_path)

    # load config
    config = config_load.load_config(conf_path)

    # print(config)

    migrate_type = ("MigrateInfo", "migrate.type")

    if migrate_type[0] not in config or migrate_type[1] not in config[migrate_type[0]]:
        print("Error: Option", migrate_type[0] + "." + migrate_type[1], "is required. ")

    traverse_functions = [ 
                           traverse_dir.traverse,
                           traverse_urllist.traverse,
                           # traverse_qiniu
                         ]

    traverse_functions[int(config[migrate_type[0]][migrate_type[1]]) - 1](config)



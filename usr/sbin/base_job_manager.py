#!/usr/bin/env python
###############################################################################
 #  Copyright (c) 2015 Tencent Inc.
 #  Distributed under the MIT license 
 #  (See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
 #  
 #  Project: Cloud Image Migration Tool
 #  Filename: base_job_manager.py
 #  Version: 2.0
 #  Author: Jamis Hoo
 #  E-mail: hoojamis@gmail.com
 #  Date: Sep  7, 2015
 #  Time: 14:29:44
 #  Description: base class of job submitting module
###############################################################################

import re
import abc
import time
import math
import sqlite3

class BaseJobManager(object):
    __metaclass__ = abc.ABCMeta

    mandatory_options = [
        ("migrateinfo", "migrate.type"),
        ("paths", "job_db_path"),
                        ]

    def __init__(self, config):
        self.config = config

        db_path = config["paths"]["job_db_path"]

        self.db_connect = sqlite3.connect(db_path)
        self.db_connect.text_factory = str
        self.db_cursor = self.db_connect.cursor()

        self.db_cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        tables = [ x[0] for x in self.db_cursor.fetchall() ]

        # create table
        # TABLE jobs
        # | fileid | status | log | src |
        # fileid: primary key
        # status: 0 -- new submitted, 1 -- successful, 2 -- failed
        # log: error log

        if "jobs" not in tables or "metadata" not in tables:
            if "jobs" in tables:
                self.db_cursor.execute("DROP TABLE jobs")
            if "metadata" in tables:
                slef.db_cursor.execute("DROP TABLE metadata")
            
            self.db_cursor.execute(
                """CREATE TABLE jobs (
                    serial INTEGER PRIMARY KEY,
                    fileid TEXT NOT NULL UNIQUE, 
                    status INT NOT NULL, 
                    src TEXT, 
                    log TEXT)
                """)
            self.db_cursor.execute("CREATE INDEX status_index ON jobs(status)")
            self.db_cursor.execute(
                """CREATE TABLE metadata ( 
                    key TEXT PRIMARY KEY NOT NULL, 
                    value TEXT)
                """)
            # compound INSERT is not supported before SQLite 3.7.11
            self.db_cursor.execute("INSERT INTO metadata VALUES ('submitted', '0')")
            self.db_cursor.execute("INSERT INTO metadata VALUES ('successful', '0')")
            self.db_cursor.execute("INSERT INTO metadata VALUES ('failed', '0')")
            self.db_cursor.execute("INSERT INTO metadata VALUES ('last_selected', '0')")
        
        self.db_cursor.execute("SELECT value FROM metadata WHERE key = 'submitted'")
        self.already_submitted = int(self.db_cursor.fetchone()[0])

        self.db_connect.commit()

        if "advanced" in config and "fileid.ignore.if" in config["advanced"]:
            self.fileid_ignore_if = re.compile(config["advanced"]["fileid.ignore.if"])
        else:
            self.fileid_ignore_if = None

        if "advanced" in config and "fileid.ignore.unless" in config["advanced"]:
            self.fileid_ignore_unless = re.compile(config["advanced"]["fileid.ignore.unless"])
        else:
            self.fileid_ignore_unless = None

        if "advanced" in config and "fileid.ignore.execute" in config["advanced"]:
            execute_codes = config["advanced"]["fileid.ignore.execute"].decode("string_escape")
            self.fileid_ignore_execute = compile(execute_codes, "<string>", "exec")
        else:
            self.fileid_ignore_execute = None

        self.exec_namespace = {}
        exec "pass" in self.exec_namespace

        self.new_submitted = 0
        self.ignore = 0
        self.submit_error = 0

        self.db_commit_interval = float(self.config["toolconfig"]["db.commit.interval"])
        self.db_last_commit = 0

    def __del__(self):
        self.db_cursor.execute(
            "UPDATE metadata SET value = ? WHERE key = 'submitted'",
            (self.already_submitted + self.new_submitted, )
        )

        self.db_connect.commit()
        self.db_connect.close()

    @staticmethod
    def check_config(config):
        for section, option in BaseJobManager.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        if "advanced" in config and "fileid.ignore.if" in config["advanced"]:
            try:
                re.compile(config["advanced"]["fileid.ignore.if"])
            except re.error:
                return "Error: Regex syntax error for Advanced.fileid.ignore.if. "

        if "advanced" in config and "fileid.ignore.unless" in config["advanced"]:
            try:
                re.compile(config["advanced"]["fileid.ignore.unless"])
            except re.error:
                return "Error: Regex syntax error for Advanced.fileid.ignore.unless. "

        if "advanced" in config and "fileid.ignore.execute" in config["advanced"]:
            execute_codes = config["advanced"]["fileid.ignore.execute"].decode("string_escape")
            try:
                compile(execute_codes, "<string>", "exec")
            except SyntaxError as e:
                return "Error: Syntax error in Advanced.fileid.ignore.execute, %s. " % execute_codes

        try:
            db_commit_interval = float(config["toolconfig"]["db.commit.interval"])
            if db_commit_interval <= 0 or math.isnan(db_commit_interval):
                return "Error: Invalid value for ToolConfig.db.commit.interval. "
        except ValueError:
            return "Error: Invalid value for ToolConfig.db.commit.interval. "
  


    def submit(self, fileid, src):
        if self.fileid_ignore_if and self.fileid_ignore_if.match(fileid):
            self.ignore += 1
            return
        if self.fileid_ignore_unless and not self.fileid_ignore_unless.match(fileid):
            self.ignore += 1
            return

        # You can give a custom function to determine whether or not to 
        # ignore this job according to the original fileid and source
        # you can also modify the original fileid or source
        # code is executed in the same namespace every time
        # variables available: 
        #   input: fileid: original fileid
        #          src: original source    
        #   output: fileid: new fileid
        #           src: new source
        #           ignore: ignore this job if this is True
        def custom_fileid_ignore_func(fileid, src, codes):
            self.exec_namespace["fileid"] = fileid
            self.exec_namespace["src"] = src
            self.exec_namespace["ignore"] = False
            exec codes in self.exec_namespace
            return (self.exec_namespace["fileid"], 
                    self.exec_namespace["src"],
                    self.exec_namespace["ignore"])

        if self.fileid_ignore_execute:
            (fileid, src, ignore) = custom_fileid_ignore_func(fileid, src, self.fileid_ignore_execute)
            if ignore:
                self.ignore += 1
                return
         
        try:
            self.db_cursor.execute(
                "INSERT INTO jobs VALUES (NULL, ?, 0, ?, NULL)", (fileid, src)
            )
        except sqlite3.Error:
            self.submit_error += 1 
        else:
            self.new_submitted += 1

        if self.db_last_commit + self.db_commit_interval < time.time():
            try:
                self.db_cursor.execute(
                    "UPDATE metadata SET value = ? WHERE key = 'submitted'",
                    (self.already_submitted + self.new_submitted, )
                )
                self.db_connect.commit()
                self.db_last_commit = time.time()
            except sqlite3.Error:
                pass 


    @abc.abstractmethod
    def do(self):
        pass

    def start(self):
        try:
            self.do()
        except KeyboardInterrupt:
            pass


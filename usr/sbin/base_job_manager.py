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
###############################################################################

import re
import abc
import sqlite3

class BaseJobManager(object):
    """
    Abstract base class of job manager.
    This module is only used in the procedure of submitting jobs.
    It creates database and submit jobs into it.

    Attributes:
        mandatory_options: Configuration options required by this class. This is
            a list of tuples each of which contains two strings, section name and 
            property name, both of which are case-insensitive.

        config: Copy of configuration

        db_connect: Connecter to sqlite3 database

        db_cursor: Cursor of db_connect

        fileid_ignore_if: Compiled regular expression if Advanced.fileid.ignore.if
            is provided in config, none otherwise.

        fileid_ignore_unless: Compiled regular expression if Advanced.fileid.ignore.unless
            is provided in config, none otherwise.

        fileid_ignore_execute: Compiled byte-code if Advanced.fileid.ignore.execute
            is provided in config, none otherwise.

        exec_namespace: Namespace to execute fileid_ignore_execute byte-code.

        new_submitted: Total number of jobs submitted.

        ignore: Total number of jobs ignored.

        submit_error: Total number jobs failed when submitting.
    """
    __metaclass__ = abc.ABCMeta

    mandatory_options = [
        ("migrateinfo", "migrate.type"),
        ("paths", "job_db_path"),
                        ]

    def __init__(self, config):
        """
        Create (if not exists) and open database, initialize other attributes.
        
        Args:
            config: configuration dict.

        """
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


    def __del__(self):
        """
        Close the database.
        The submitting procedure should be atomic. That is, all or none of the 
        jobs should be submitted into database. So we shouldn't call commit in
        this function.
        """
        self.db_connect.close()

    @staticmethod
    def check_config(config):
        """
        Check whether all required options are provided. 
        Also check the validity of some options.

        Args:
            config: configuration dict

        Returns:
            Returns string containing error message if there are some errors.
            Returns none otherwise.
        """

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


    def submit(self, fileid, src):
        """
        Accept a job identified by file id and src, determine whether this job 
        should be ignored, submit it to database and update counters (num_submitted, 
        submit_error, ignore).

        Args:
            fileid: File id of the job. This should be unique among all jobs or 
                set it none.
            src: Source of this job. This can be a URL or a local filename or 
                identifier of a resource in any other forms that can be 
                recognized by slave.

        Returns: Returns none.
        """


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

    @abc.abstractmethod
    def do(self):
        """
        Interface which should be implemented in derived class.
        This function should submit some jobs by calling submit().
        DO NOT raise exceptions other than KeyboardInterrupt.
        """
        pass

    def start(self):
        """
        Start submitting jobs.
        This function will call do(), which should be implemented in derived 
        class. Submitted jobs will be commited to database only if do() normally
        returns.

        """
        try:
            self.do()
            self.db_cursor.execute(
                "UPDATE metadata SET value = value + ? WHERE key = 'submitted'",
                (self.new_submitted, )
            )
            self.db_connect.commit()
        except KeyboardInterrupt:
            self.new_submitted = 0
            self.submit_error = 0
            self.ignore = 0

#!/usr/bin/env python

from __future__ import print_function

import abc
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
                    serial INT PRIMARY KEY NOT NULL,
                    fildid TEXT, 
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
            self.db_cursor.execute(
                """INSERT INTO metadata VALUES 
                    ('submitted', '0'),
                    ('successful', '0'),
                    ('failed', '0'),
                    ('last_selected', '0')
                """)

        self.db_connect.commit()

        self.new_submitted = 0
        self.submit_error = 0

    def __del__(self):
        self.db_cursor.execute(
            "UPDATE metadata SET value = value + ? WHERE key = 'submitted'", (self.new_submitted, )
        )

        self.db_connect.commit()
        self.db_connect.close()

    @staticmethod
    def check_config(config):
        for section, option in BaseJobManager.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        return None

    def submit(self, fileid, src):
        #TODO: filter
        #print("get submit: %s, %s" % (fileid, src))
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
        pass

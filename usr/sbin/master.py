#!/usr/bin/env python

from __future__ import print_function
import os
import signal
import multiprocessing
import sqlite3
from collections import deque

class Master(object):

    mandatory_options = [
        ("paths", "job_db_path"),
        ("toolconfig", "concurrency"),
                        ]
    
    def __init__(self, config, SlaveClass, UploaderClass):
        self.config = config
        self.SlaveClass = SlaveClass
        self.UploaderClass = UploaderClass

        db_path = config["paths"]["job_db_path"]

        self.db_connect = sqlite3.connect(db_path)
        self.db_connect.text_factory = str
        self.db_cursor = self.db_connect.cursor()

        # if all jobs have already been traversed, set the cursor to start
        # so as to retry all failed jobs
        # else set cursor to the first job not attempted yet
        self.db_cursor.execute(
        """UPDATE metadata SET value = 
            (SELECT 
                COALESCE(
                    (SELECT serial FROM jobs WHERE status = 0 ORDER BY serial LIMIT 1), 
                    1) 
                - 1)
            WHERE key = 'last_selected'
        """
        )
        self.db_connect.commit()

        self.no_more_jobs = False


    def __del__(self):
        self.db_connect.commit()
        self.db_connect.close()


    @staticmethod
    def check_config(config):
        for section, option in Master.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        if not config["toolconfig"]["concurrency"].isdigit() or int(config["toolconfig"]["concurrency"]) <= 0:
            return "Error: Minumums of ToolConfig.concurrency is 1. "
        
        db_path = config["paths"]["job_db_path"]
        if os.path.isfile(db_path):
            connect = sqlite3.connect(db_path)
            cursor = connect.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            tables = [ x[0] for x in cursor.fetchall() ]

            try:
                if "jobs" not in tables:
                    return "Error: table jobs does not exist. "
                if "metadata" not in tables:
                    return "Error: table metadata does not exist. "
            finally:
                connect.close()

    def create_slaves(self):
        num_slaves = int(self.config["toolconfig"]["concurrency"])
        self.slaves = []
        self.job_queue = multiprocessing.Queue()
        self.log_queue = multiprocessing.Queue()


        for _ in range(num_slaves):
            slave_class = self.SlaveClass(self.config, self.UploaderClass)
            slave = multiprocessing.Process(target = slave_class.start, args = (self.job_queue, self.log_queue))
            slave.daemon = True
            slave.start()

            self.slaves.append(slave)

    def write_log(self, (serial, fileid, status, log)):
        self.db_cursor.execute(
            "UPDATE jobs SET status = ?, fileid = ?, log = ? WHERE serial = ?", (status, fileid, log, serial)
        )

        self.db_cursor.execute(
            "UPDATE metadata SET value = value + 1 WHERE key = ?", ("successful" if status == 1 else "failed",)
        )

    def load_job(self):
        if self.job_queue_buffer: return
        # TODO: This makes it impossible to upload while submitting jobs
        if self.no_more_jobs: return

        self.db_cursor.execute(
            """SELECT serial, fileid, src 
                FROM jobs 
                WHERE status <> 1 AND 
                      serial > (SELECT value FROM metadata WHERE key == 'last_selected') 
                ORDER BY serial 
                LIMIT ?""", (self.job_queue_buffer_max_size,)
        )
        for job in self.db_cursor.fetchall():
            self.job_queue_buffer.append(job)

        if self.job_queue_buffer:
            last_selected = self.job_queue_buffer[-1][0]
            self.db_cursor.execute(
                "UPDATE metadata SET value = ? where key = 'last_selected'", (last_selected,)
            )
        else:
            self.job_queue_buffer.extend([ "no more jobs" ] * len(self.slaves))
            self.no_more_jobs = True


    def fill_job_queue(self):
        for _ in range(self.job_queue_max_size - self.job_queue_size):
            if not self.job_queue_buffer:
                self.load_job()
                if not self.job_queue_buffer:
                    break
            self.job_queue.put(self.job_queue_buffer.popleft())
            self.job_queue_size += 1

    def start(self):
        signal.signal(signal.SIGINT, lambda signum, frame: None)        

        self.create_slaves()

        self.job_queue_size = 0
        self.job_queue_max_size = 500
        # TODO: move constans to config
        self.job_queue_buffer = deque()
        self.job_queue_buffer_max_size = 100000

        num_quit = 0
        
        while True:
            # fill job queue
            if self.job_queue_size < 200:
                self.fill_job_queue() 
            # fetch a log
            log = self.log_queue.get()
            print("get looooog:", log)
            # handle log
            if log == "quit":
                num_quit += 1
                if num_quit == len(self.slaves):
                    break
            else:
                self.write_log(log)
            self.job_queue_size -= 1
        
        for slave in self.slaves:
            slave.join()

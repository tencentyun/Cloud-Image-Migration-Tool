#!/usr/bin/env python

from __future__ import print_function
import os
import signal
import re
import math
import time
import multiprocessing
import sqlite3
from collections import deque

class Master(object):

    mandatory_options = [
        ("paths", "job_db_path"),
        ("toolconfig", "concurrency"),
        ("toolconfig", "jobqueue.capacity"),
        ("toolconfig", "jobqueue.reload.threshold"),
        ("toolconfig", "buffer.size"),
        ("toolconfig", "db.commit.interval"),
                        ]
    
    def __init__(self, config, SlaveClass, UploaderClass):
        self.config = config
        self.SlaveClass = SlaveClass
        self.UploaderClass = UploaderClass

        self.db_connect = None
        self.db_cursor = None

        if "advanced" in config and "error.ignore.if" in config["advanced"]:
            self.ignore_error_if = re.compile(config["advanced"]["error.ignore.if"])
        else:
            self.ignore_error_if = None

    # There's a bug on OS X when using urllib with multiprocessing and sqlite3
    # So this function cannot be called before create_slaves
    # references:
    # http://bugs.python.org/issue9405
    # http://bugs.python.org/issue13829
    def init_db(self):
        db_path = self.config["paths"]["job_db_path"]

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
        self.db_commit_interval = float(self.config["toolconfig"]["db.commit.interval"])
        self.db_last_commit = 0

    def __del__(self):
        if self.db_connect:
            self.db_connect.commit()
            self.db_connect.close()

    @staticmethod
    def check_config(config):
        for section, option in Master.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        if not config["toolconfig"]["concurrency"].isdigit() or int(config["toolconfig"]["concurrency"]) <= 0:
            return "Error: Minumums of ToolConfig.concurrency is 1. "

        if not config["toolconfig"]["jobqueue.capacity"].isdigit() or int(config["toolconfig"]["jobqueue.capacity"]) <= 0:
            return "Error: Minimums of ToolConfig.jobqueue.capacity is 1. "

        try:
            reload_th = float(config["toolconfig"]["jobqueue.reload.threshold"])
            if reload_th <= 0 or reload_th > 1:
                return "Error: ToolConfig.jobqueue.reload.threshold should within range (0, 1]. "
        except ValueError:
            return "Error: ToolConfig.jobqueue.reload.threshold should within range (0, 1]. "

        try:
            db_commit_interval = float(config["toolconfig"]["db.commit.interval"])
            if db_commit_interval <= 0 or math.isnan(db_commit_interval):
                return "Error: Invalid value for ToolConfig.db.commit.interval. "
        except ValueError:
            return "Error: Invalid value for ToolConfig.db.commit.interval. "
        
        if not config["toolconfig"]["buffer.size"].isdigit() or int(config["toolconfig"]["buffer.size"]) <= 0:
            return "Error: Minimums of ToolConfig.buffer.sizeis 1. "

        if "advanced" in config and "error.ignore.if" in config["advanced"]:
            try:
                re.compile(config["advanced"]["error.ignore.if"])
            except re.error:
                return "Error: Regex syntax error for Advanced.error.ignore.if. "

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

    def write_log(self, (serial, fileid, old_status, status, log)):
        self.db_cursor.execute(
            "UPDATE jobs SET status = ?, fileid = ?, log = ? WHERE serial = ?", (status, fileid, log, serial)
        )

        if status == 1 and old_status == 0:
            update_values = [ (1, "successful") ]
        elif status == 1 and old_status == 2:
            update_values = [ (1, "successful"), (-1, "failed") ]
        elif status == 2 and old_status == 0:
            update_values = [ (1, "failed") ]
        elif status == 2 and old_status == 2:
            update_values = [ ]
        else:
            print("Error: should not happen")

        self.db_cursor.executemany(
            "UPDATE metadata SET value = value + ? WHERE key = ?", update_values
        )

        if self.db_last_commit + self.db_commit_interval < time.time():
            try:
                self.db_connect.commit()
                self.db_last_commit = time.time()
            except sqlite3.Error:
                pass 

    def load_job(self):
        if self.job_queue_buffer: return
        if self.no_more_jobs: return

        self.db_cursor.execute(
            """SELECT serial, fileid, status, src, log
                FROM jobs 
                WHERE status <> 1 AND 
                      serial > (SELECT value FROM metadata WHERE key = 'last_selected') 
                ORDER BY serial 
                LIMIT ?""", (self.job_queue_buffer_max_size,)
        )
        
        last_selected = None
        for job in self.db_cursor.fetchall():
            job_serial = job[0]
            job_log = job[4]
            job_info = job[: -1]

            if self.ignore_error_if and job_log and self.ignore_error_if.match(job_log):
                continue

            self.job_queue_buffer.append(job_info)
            last_selected = job_serial

        if last_selected is not None:
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
        if not os.path.isfile(self.config["paths"]["job_db_path"]):
            print("Job database not found, nothing to do. ")
            return

        def interrupt_subprocesses(signum, frame):
            for process in self.slaves:
                os.kill(process.pid, signal.SIGINT)

        signal.signal(signal.SIGINT, interrupt_subprocesses)

        self.create_slaves()

        self.init_db()

        self.job_queue_size = 0
        self.job_queue_max_size = int(self.config["toolconfig"]["jobqueue.capacity"])
        self.job_queue_buffer = deque()
        self.job_queue_buffer_max_size = int(self.config["toolconfig"]["buffer.size"])
        self.job_queue.reload_size = self.job_queue_max_size * float(self.config["toolconfig"]["jobqueue.reload.threshold"])

        num_quit = 0
        
        while True:
            # fill job queue
            if self.job_queue_size < self.job_queue.reload_size:
                self.fill_job_queue() 
            # fetch a log
            log = self.log_queue.get()
            # handle log
            if log == "quit":
                num_quit += 1
                if num_quit == len(self.slaves):
                    break
            else:
                self.write_log(log)
            self.job_queue_size -= 1

        self.db_connect.commit()

        self.job_queue.cancel_join_thread()
        self.log_queue.cancel_join_thread()

        for slave in self.slaves:
            slave.join()
        

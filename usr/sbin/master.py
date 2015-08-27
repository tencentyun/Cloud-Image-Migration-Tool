#!/usr/bin/env python

import sqlite3
import multiprocessing

class Master(object):

    mandatory_options = [
        ("paths", "job_db_path"),
        ("toolconfig", "concurrency"),
                        ]
    
    def __init__(self, config):
        self.config = config

        db_path = config["paths"]["job_db_path"]

        self.db_connect = sqlite3.connect(db_path)
        self.db_connect.text_factory = str
        self.db_cursor = self.db_connect.cursor()

        # if all jobs have already been traversed, set the cursor to start
        # so as to retry all failed jobs
        self.db_cursor.execute(
        """UPDATE metadata SET value = 
            (CASE WHEN 
                (SELECT COUNT(*) 
                    FROM jobs 
                    WHERE status == 0 AND 
                          serial > (SELECT value FROM metadata WHERE key == "last_selected")) <> 0 
                THEN value 
                ELSE 0 
            END) 
            WHERE key = 'last_selected';"""
        )
        selc.db_connect.commit()

        self.no_more_jobs = False

        self.create_slaves()


    def __del__(self):
        self.db_connect.close()

        # TODO: temrinate slave processes

    @staticmethod
    def check_config(config):
        for section, option in Master.mandatory_options:
            if section not in config or option not in config[section]:
                return "Error: Option %s.%s is required. " % (section, option)

        if not config["toolconfig"]["concurrency"].isdigit() or int(config["toolconfig"]["concurrency"]) <= 0:
            return "Error: Minumums of ToolConfig.concurrency is 1. "
        
        db_path = config["paths"]["job_db_path"]
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
        num_slaves = int(config["toolconfig"]["concurrency"])
        self.slaves = []
        self.job_queue = multiprocessing.Queue()
        self.log_queue = multiprocessing.Queue()

        for i in range(num_slaves):
            slave = multiprocessing.Process(target = None, args = None)
        slave.daemon = True
        slave.start()

        self.slaves.append(slave)

    def write_log(self, (fileid, status, log)):
        self.job_queue_size -= 1

        self.db_cursor.execute(
            "UPDATE jobs SET status = ?, log = ? WHERE fileid = ?", (fileid, status, log)
        )

        self.db_cursor.execute(
            "UPDATE metadata SET value = value + 1 WHERE key = ?", "successful" if status == 1 else "failed"
        )

    def load_job(self):
        if self.job_queue_buffer: return
        # TODO: This makes it impossible to upload while submitting jobs
        if self.no_more_jobs: return

        self.db_connect.commit()
        self.db_cursor.execute(
            """SELECT serial, fileid, src 
                FROM jobs 
                WHERE status <> 1 AND 
                      serial > (SELECT value FROM metadata WHERE key == 'last_selected') 
                ORDER BY serial 
                LIMIT ?""", self.job_queue_buffer_max_size
        )
        for job in self.db_cursor.fetchall():
            self.job_queue_buffer.append(job)
        self.job_queue_buffer.reverse()

        if self.job_queue_buffer:
            last_selected = self.job_queue_buffer[0][0]
            self.db_cursor.execute(
                "UPDATE metadata SET value = ? where key = 'last_selected'", last_selected
            )
        else:
            job_queue_buffer.extend([ "no more jobs" ] * len(self.slaves))
            self.no_more_jobs = True

        self.db_connect.commit()

    def fill_job_queue(self):
        self.job_queue_size = 0
        self.job_queue_max_size = 300
        # move constans to config
        # TODO: use deque
        self.job_queue_buffer = []
        self.job_queue_buffer_max_size = 100000

        for _ in range(self.job_queue_max_size - self.job_queue_size):
            if not self.job_queue_buffer:
                self.load_job()
                if not self.job_queue_buffer:
                    break
            self.job_queue.put(self.job_queue_buffer.pop())

    def start(self);
        self.create_slaves()

        num_quit = 0
        
        while True:
            # fill job queue
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
        
        for slave in self.slaves:
            slave.join()

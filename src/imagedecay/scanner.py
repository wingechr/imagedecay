#!/usr/bin/env python3
# coding=utf-8
"""Scan folder for new files
"""

import logging
import os
import re
import time
from threading import Thread


class Scanner(Thread):
    """
    Scan a directory periodically for new files matching a pattern and call a given function
    """
    def __init__(self, queue, path, interval_s, file_pattern='.*\.py'):
        super().__init__(target=self.run, daemon=False)
        self.queue = queue
        self.path = path
        self.interval_s = float(interval_s)
        self.file_pattern = re.compile(file_pattern, re.IGNORECASE)
        self.running = False
        self.files = set()

    def run(self):
        logging.debug("SCAN started on %s" % self.path)
        while self.running:
            logging.debug("SCAN scanning")
            files = set(x for x in os.listdir(self.path) if self.file_pattern.match(x))
            new_files = files - self.files
            if new_files:
                # sort by date
                new_files_with_path = [os.path.join(self.path, f) for f in new_files]
                new_files_by_mtime = [(os.path.getmtime(f), f) for f in new_files_with_path]
                latest = sorted(new_files_by_mtime, reverse=True)[0][1]
                logging.debug('SCAN queue new file %s' % latest)
                # put only the latest file into the queue
                self.queue.put(latest)
                self.files = self.files | new_files
            time.sleep(self.interval_s)
        self.queue.put(None)
        logging.debug("SCAN stopped")

    def start(self):
        """
        Start scan process in new thread
        """
        self.running = True
        super().start()

    def stop(self):
        self.running = False


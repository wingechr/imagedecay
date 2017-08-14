# coding=utf-8
"""Scan folder for new files."""

import logging
import os
import re
import time
from imagedecay.thread import MyThread

class Scanner(MyThread):
    """Scan a directory periodically for new files matching a pattern and call a given function."""
    def __init__(self, queue, path, interval_s, file_pattern=r'.*\.py'):
        super().__init__()
        self.queue = queue
        self.path = path
        self.interval_s = float(interval_s)
        self.file_pattern = re.compile(file_pattern, re.IGNORECASE)
        self.files = self.get_files()
        self.threads = list()

    def run(self):
        """Main thread."""
        logging.info("SCAN START %s", self.path)
        while self.running:
            logging.debug("SCAN SCANNING")
            files = self.get_files()
            new_files = files - self.files
            if new_files:
                # sort by date
                new_files_with_path = [os.path.join(self.path, f) for f in new_files]
                new_files_by_mtime = [(os.path.getmtime(f), f) for f in new_files_with_path]
                new_files_by_mtime = list(sorted(new_files_by_mtime, reverse=True))
                latest = new_files_by_mtime[0][1]
                for dummy_ctime, filename in new_files_by_mtime[1:]:
                    logging.info('SCAN SKIP %s', filename)
                logging.info('SCAN ADD %s', latest)
                self.queue.put(latest)  # put in path
                self.files = self.files | new_files
            time.sleep(self.interval_s)
        logging.info("SCAN STOP")

    def get_files(self):
        """get current list of files in directory."""
        return set(x for x in os.listdir(self.path) if self.file_pattern.match(x))

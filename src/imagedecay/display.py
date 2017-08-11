#!/usr/bin/env python3
# coding=utf-8
"""Display series of images
"""

import logging
import time
from threading import Thread


class Display(Thread):
    """
    Scan a directory periodically for new files matching a pattern and call a given function
    """
    def __init__(self, queue_in, queue_out, interval_s):
        super().__init__(target=self.run, daemon=False)
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.interval_s = float(interval_s)
        self.image_list = None
        self.image_index = -1
        self.current_image = None


    def run(self):

        logging.debug("DISP started")
        while self.running:
            # remove all items from queue (so there is no backlog)
            while not self.queue_in.empty():
                self.image_list = self.queue_in.get()
                self.image_index = -1
                #if self.image_list is None:
                #    break
                logging.debug('DISP new list')
            if self.image_list:
                # show next image from list
                self.image_index = (self.image_index + 1) % len(self.image_list)
                image = self.image_list[self.image_index]
                logging.debug('DISP show %s' % image)
                self.queue_out.put(image)
            else:
                self.queue_out.put(None)  # signal to draw black screen
            time.sleep(self.interval_s)
        logging.debug("DISP stopped")

    def start(self):
        """
        Start display process in new thread
        """
        self.running = True
        self.image_list = None
        self.image_index = -1
        self.current_image = None
        super().start()

    def stop(self):
        self.running = False



# coding=utf-8
"""Control the image display queue."""

import logging
import time

from imagedecay.thread import MyThread


class Display(MyThread):
    """Control the image display queue."""
    def __init__(self, queue_in, queue_out, interval_s=1.0):
        super().__init__()
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.interval_s = interval_s
        self.wait_interval_s = 0.1
        self.image_list = list()
        self.image_queue = list()
        self.image_index = -1
        self.last_update = 0
        self.is_waiting = False

    def run(self):
        """Main thread."""
        logging.debug("DISP START")
        while self.running:
            next_item = self.queue_in.get_first_nowait()
            if isinstance(next_item, str):  # queue
                self.image_queue.append(next_item)
            elif isinstance(next_item, list):
                self.image_list = list(next_item)
                self.image_index = -1
                if not self.image_list:  # if its an empty list == new image: clear queue
                    self.image_queue = list()
            if time.time() - self.last_update > self.interval_s:
                # time to send a new image
                if self.image_queue:  #
                    self._send_next(self.image_queue[0])
                    self.image_queue = self.image_queue[1:]
                elif self.image_list:
                    self.image_index = (self.image_index + 1) % len(self.image_list)
                    self._send_next(self.image_list[self.image_index])
                else:
                    if not self.is_waiting:
                        logging.info("DISP WAITING")
                    self.is_waiting = True
            time.sleep(self.wait_interval_s)
        logging.debug("DISP STOP")

    def _send_next(self, img):
        self.is_waiting = False
        self.queue_out.put(img)
        self.last_update = time.time()

    def stop(self):
        """Stop the thread."""
        super().stop()
        self.queue_in.put(None)  # break busy waiting

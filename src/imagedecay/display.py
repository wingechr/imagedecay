# coding=utf-8
"""Control the image display queue."""

import logging
from threading import Thread


class Display(Thread):
    """Control the image display queue."""
    def __init__(self, queue_in):
        super().__init__(target=self.run, daemon=False)
        self.queue_in = queue_in
        self.image_list = list()
        self.image_index = -1
        self.running = False

    def run(self):
        """Main thread."""
        logging.debug("DISP START")
        while self.running:
            self.image_list = self.queue_in.get()
            if self.image_list == []:
                logging.debug('DISP NEW')
                self.image_index = -1
            # remove all items from queue (so there is no backlog)
            while not self.queue_in.empty():
                self.image_list = self.queue_in.get()
                if self.image_list is None:
                    break
                elif self.image_list == []:
                    logging.debug('DISP NEW')
                    self.image_index = -1
            if self.image_list is None:
                break
        logging.debug("DISP STOP")

    def start(self):
        """Start the thread."""
        self.running = True
        super().start()

    def stop(self):
        """Stop the thread."""
        self.running = False

    def get_next(self):
        """Get the image to display."""
        if not self.image_list:
            image = ''
        else:
            self.image_index = (self.image_index + 1) % len(self.image_list)
            image = self.image_list[self.image_index]
        logging.debug('DISP RETURN %d %s', self.image_index, image)
        return image



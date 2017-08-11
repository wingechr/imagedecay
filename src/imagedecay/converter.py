#!/usr/bin/env python3
# coding=utf-8
"""Display series of images
"""

import logging
import os
from threading import Thread
from imagedecay.readwrite import read, write
from imagedecay.filter import apply_filterconf


class Converter(Thread):
    """
    Scan a directory periodically for new files matching a pattern and call a given function
    """
    def __init__(self, queue_in, queue_out, path, conf, n_iter, save_steps=0):
        super().__init__(target=self.run, daemon=False)
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.path = path
        self.conf = conf
        self.n_iter = n_iter
        self.save_steps = save_steps
        self.running = False

    def run(self):
        logging.debug("CONV started")
        while self.running:
            # wait on queue for next input
            filepath = self.queue_in.get()
            if filepath is None:
                break
            logging.debug("CONV new img: %s" % type(filepath))
            # load image
            im_array, meta = read(filepath)
            imagelist = list()
            # save original
            filepath_out = self.get_output_filename(filepath, 0)
            write(im_array, filepath_out)
            imagelist.append(filepath_out)
            for i in range(1, self.n_iter + 1):
                logging.debug('STEP % 5d' % i)
                # apply filter
                im_array = apply_filterconf(im_array, self.conf)
                # save
                if i == self.n_iter or (self.save_steps and i % self.save_steps == 0):
                    filepath_out = self.get_output_filename(filepath, i)
                    write(im_array, filepath_out)
                    imagelist.append(filepath_out)
            if imagelist:
                imagelist = tuple(imagelist)
                logging.debug('CONV queueing %d' % len(imagelist))
                self.queue_out.put(imagelist)
        self.queue_out.put(None)
        logging.debug("CONV stopped")

    def start(self):
        """
        Start conversion process in new thread
        """
        self.running = True
        super().start()

    def stop(self):
        self.running = False

    def get_output_filename(self, filepath, i):
        filename = os.path.basename(filepath)
        path = os.path.join(self.path, '%s.%06d.png' % (filename, i))
        return path




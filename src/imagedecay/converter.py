#!/usr/bin/env python3
# coding=utf-8
"""Display series of images
"""

import logging
import os
from threading import Thread
from imagedecay.readwrite import read, write
from imagedecay.filter import apply_filterconf
from skimage.transform import rescale

class Converter(Thread):
    """
    Scan a directory periodically for new files matching a pattern and call a given function
    """
    def __init__(self, queue_in, queue_out, path, conf, n_iter, save_steps, max_image_size, output_fmt='bmp', publish_steps=True):
        super().__init__(target=self.run, daemon=False)
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.path = path
        self.conf = conf
        self.n_iter = n_iter
        self.save_steps = save_steps
        self.running = False
        self.max_image_size = max_image_size
        self.output_fmt = output_fmt
        self.publish_steps = publish_steps
        self.imagelist = list()

    def resize(self, img):
        sx = self.max_image_size[0] / img.shape[1]
        sy = self.max_image_size[1] / img.shape[0]
        s = min(sx, sy)
        img2 = rescale(img, s, mode='constant')
        logging.info('CONV RESCALE (%d x %d) - %0.2f -> (%d x %d)' % (img.shape[0], img.shape[1], s, img2.shape[0], img2.shape[1]))
        return img2

    def run(self):
        logging.info("CONV START")
        while self.running:
            # wait on queue for next input
            filepath = self.queue_in.get()
            # now iterate until last item:
            while not self.queue_in.empty():
                logging.info("CONV SKIP %s" % filepath)
                filepath = self.queue_in.get()
            if filepath is None:
                break
            logging.info("CONV NEW %s" % filepath)
            self.queue_out.put([])
            # load image
            im_array, meta = read(filepath)
            # resize image
            im_array = self.resize(im_array)
            self.imagelist = list()
            # save original
            filepath_out = self.get_output_filename(filepath, 0)
            write(im_array, filepath_out)
            self.imagelist.append(filepath_out)
            if self.publish_steps:
                logging.info("CONV SHOW %s" % filepath_out)
                self.queue_out.put(self.imagelist)
            for i in range(1, self.n_iter + 1):
                if not self.queue_in.empty():
                    logging.info('CONV CANCEL')
                    continue
                logging.debug('CONV STEP %5d' % i)
                # apply filter
                im_array = apply_filterconf(im_array, self.conf)
                # save
                if i == self.n_iter or (self.save_steps and i % self.save_steps == 0):
                    filepath_out = self.get_output_filename(filepath, i)
                    logging.debug("CONV SAVE %s" % filepath_out)
                    write(im_array, filepath_out)
                    # publish right away
                    self.imagelist.append(filepath_out)
                    if self.publish_steps:
                        logging.info("CONV SHOW %s" % filepath_out)
                        self.queue_out.put(self.imagelist)
            # publish list if sequence finished
            self.link_last_img(filepath_out)
            if not self.publish_steps:
                logging.info("CONV SHOW ALL")
                self.queue_out.put(self.imagelist)
        self.queue_out.put(None)
        logging.info("CONV STOP")

    def link_last_img(self, imgpath):
        if not imgpath:
            return
        logging.info("CONV LINK %s" % imgpath)
        imgpath = os.path.basename(imgpath)
        pass  # TODO

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
        path = os.path.join(self.path, '%s.%06d.%s' % (filename, i, self.output_fmt))
        return path

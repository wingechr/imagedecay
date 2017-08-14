#!/usr/bin/env python3
# coding=utf-8
"""Image conversion functions and script."""

import logging
import os

from skimage.transform import rescale
from imagedecay.readwrite import read, write
from imagedecay.filter import apply_filterconf
from imagedecay.thread import MyThread, main_setup

CMD_ARGS = [  # list of pairs of (args_tuple, kwargs_dict)
    (['source_image'], {
        'help': 'path source images',
        'type': str
    }),
    (['filtername'], {
        'help': 'name of the filter',
    })
]


class Converter(MyThread):
    """Scan a directory periodically for new files matching a pattern and call a given function."""
    def __init__(self, queue_in, queue_out, path, conf, n_iter, save_steps, max_image_size,
                 output_fmt='bmp', publish_steps=True, list_index='index.html'):
        super().__init__()
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.path = path
        self.conf = conf
        self.n_iter = n_iter
        self.save_steps = save_steps
        self.max_image_size = max_image_size
        self.output_fmt = output_fmt
        self.publish_steps = publish_steps
        self.imagelist = list()
        self.list_index = list_index

    def resize(self, img):
        """Resize the given image.

        Args:
            img (array): input image

        Returns:
            image array
        """
        scale_x = self.max_image_size[0] / img.shape[1]
        scale_y = self.max_image_size[1] / img.shape[0]
        scale = min(scale_x, scale_y)
        img2 = rescale(img, scale, mode='constant')
        logging.info('CONV RESCALE (%d x %d) - %0.2f -> (%d x %d)', img.shape[0], img.shape[1],
                     scale, img2.shape[0], img2.shape[1])
        return img2

    def run(self):
        """Main thread."""
        logging.info("CONV START")
        template = '<hml>\n<head>\n<link href="style.css" rel="stylesheet">\n</head>\n<body>\n'
        self.write_to_list_index(template, append=False)
        while self.running:
            # wait on queue for next input
            filepath = self.queue_in.get()
            # now iterate until last item:
            while not self.queue_in.empty():
                logging.info("CONV SKIP %s", filepath)
                filepath = self.queue_in.get()
            if filepath is None:
                break
            logging.info("CONV NEW %s", filepath)
            self.queue_out.put([])
            # load image
            im_array, dummy_meta = read(filepath)
            # resize image
            im_array = self.resize(im_array)
            self.imagelist = list()
            # save original
            filepath_out = self.get_output_filename(filepath, 0)
            write(im_array, filepath_out)
            self.imagelist.append(filepath_out)
            if self.publish_steps:
                logging.info("CONV SHOW %s", filepath_out)
                self.queue_out.put([filepath_out])
            canceled = False
            for i in range(1, self.n_iter + 1):
                if not self.queue_in.empty():
                    logging.info('CONV CANCEL')
                    canceled = True
                    break
                logging.debug('CONV STEP %5d', i)
                # apply filter
                im_array = apply_filterconf(im_array, self.conf)
                # save
                if i == self.n_iter or (self.save_steps and i % self.save_steps == 0):
                    filepath_out = self.get_output_filename(filepath, i)
                    logging.debug("CONV SAVE %s", filepath_out)
                    write(im_array, filepath_out)
                    # publish right away
                    self.imagelist.append(filepath_out)
                    if self.publish_steps:
                        logging.info("CONV SHOW %s", filepath_out)
                        self.queue_out.put([filepath_out])
            # publish list if sequence finished
            if not canceled:
                self.link_last_img(filepath_out)
                logging.info("CONV SHOW ALL")
                self.queue_out.put([])
                self.queue_out.put(self.imagelist)
        self.queue_out.put(None)
        self.write_to_list_index('\n</body>\n</hml>')
        logging.info("CONV STOP")

    def link_last_img(self, imgpath):
        """Add link to final image to index.html."""
        if not imgpath:
            return
        logging.info("CONV LINK %s", imgpath)
        imgpath = os.path.basename(imgpath)
        imgpath = imgpath.replace('\\', '/')
        self.write_to_list_index('<img src="%s"></img>' % imgpath)

    def get_output_filename(self, filepath, i):
        """Get filename for basename and index."""
        filename = os.path.basename(filepath)
        path = os.path.join(self.path, '%s.%06d.%s' % (filename, i, self.output_fmt))
        return path

    def write_to_list_index(self, text, append=True):
        """Write text to index.html.

        Args:
            append (bool): create new file if False
        """
        with open(self.list_index, 'a' if append else 'w', encoding='utf-8') as file:
            file.write(text)


def main(source_image, filtername, **filterargs):
    """Entry point for main script."""
    # load image
    target_image = source_image + "_" + filtername
    for key, val in sorted(filterargs.items()):
        target_image += '_%s=%.3f' % (key, val)
    target_image += ".png"
    im_array, dummy_meta = read(source_image)
    conf = [
        {
            "name": filtername,
            "kwargs": filterargs
        }
    ]
    im_array = apply_filterconf(im_array, conf)
    write(im_array, target_image)


if __name__ == '__main__':
    main_setup(main, cmd_args=CMD_ARGS, default_loglevel='WARNING')

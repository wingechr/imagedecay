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
import configargparse
from imagedecay.filter import get_conf
import sys

DEFAULT_LOGLEVEL = 'WARNING'

CMD_ARGS = [  # list of pairs of (args_tuple, kwargs_dict)
    (['source_image'], {
        'help': 'path source images',
        'type': str
    }),
    (['filtername'], {
        'help': 'name of the filter',
    })
]


class Converter(Thread):
    """
    Scan a directory periodically for new files matching a pattern and call a given function
    """
    def __init__(self, queue_in, queue_out, path, conf, n_iter, save_steps, max_image_size, output_fmt='bmp', publish_steps=True, list_index='index.html'):
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
        self.list_index = list_index

    def resize(self, img):
        sx = self.max_image_size[0] / img.shape[1]
        sy = self.max_image_size[1] / img.shape[0]
        s = min(sx, sy)
        img2 = rescale(img, s, mode='constant')
        logging.info('CONV RESCALE (%d x %d) - %0.2f -> (%d x %d)' % (img.shape[0], img.shape[1], s, img2.shape[0], img2.shape[1]))
        return img2

    def run(self):
        logging.info("CONV START")
        self.write_to_list_index('<hml>\n<head>\n<link href="style.css" rel="stylesheet">\n</head>\n<body>\n', append=False)
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
                self.queue_out.put([filepath_out])
            canceled=False
            for i in range(1, self.n_iter + 1):
                if not self.queue_in.empty():
                    logging.info('CONV CANCEL')
                    canceled = True
                    break
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
        if not imgpath:
            return
        logging.info("CONV LINK %s" % imgpath)
        imgpath = os.path.basename(imgpath)
        imgpath = imgpath.replace('\\', '/')
        self.write_to_list_index('<img src="%s"></img>' % imgpath)

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

    def write_to_list_index(self, text, append=True):
        with open(self.list_index, 'a' if append else 'w', encoding='utf-8') as f:
            f.write(text)

# test filter on one file
def main(source_image, filtername, **filterargs):
    # load image
    target_image = source_image + "_" + filtername
    for k, v in sorted(filterargs.items()):
        target_image += '_%s=%.3f' % (k, v)
    target_image += ".png"

    im_array, meta = read(source_image)
    conf = [
        {
            "name": filtername,
            "kwargs": filterargs
        }
    ]
    im_array = apply_filterconf(im_array, conf)
    write(im_array, target_image)


if __name__ == '__main__':
    # command line > environment variables > config file values > defaults
    ap = configargparse.ArgParser(
        default_config_files=[],     # add config files here
        add_config_file_help=False,  # but dont show help about the syntax
        auto_env_var_prefix=None,    # use environment variables without prefix (None for not using them)
        add_env_var_help=False       # but dont show help about that either
    )
    ap.add('--loglevel', '-l', type=str, default=DEFAULT_LOGLEVEL, help='ERROR, WARNING, INFO, or DEBUG')
    # add additional arguments
    for a in CMD_ARGS:
        ap.add(*a[0], **a[1])
    # parse and make a dictionary
    args, unknown = ap.parse_known_args()
    settings = vars(args)
    loglevel = settings.pop('loglevel')
    # create dictionary of all excess args,
    # that come in pairs of --key, val
    for i in range(len(unknown) // 2):
        k = unknown[i*2].replace('--', '')
        v = float(unknown[i * 2 + 1])
        settings[k] = v
    # reset basic config, set loglevel
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(format='[%(asctime)s %(funcName)s %(levelname)s] %(message)s',
                        level=getattr(logging, loglevel.upper()))
    logging.debug('ARGUMENTS:\n' + ap.format_values())

    # main wrapper
    rc = 0
    try:
        main(**settings)
    except KeyboardInterrupt:
        rc = 130
    except Exception as e:  # unhandled Exception
        logging.error(e, exc_info=e)  # show error trace
        rc = 1
    sys.exit(rc)

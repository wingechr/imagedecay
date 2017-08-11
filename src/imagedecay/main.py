#!/usr/bin/env python3
# coding=utf-8
"""Main script for the imagedecay package.
"""

import logging
import configargparse
import sys
from imagedecay.filter import get_conf
from imagedecay.scanner import Scanner
from imagedecay.display import Display
from imagedecay.converter import Converter
from queue import Queue
import os
import time
import pygame as pyg
from pygame.locals import QUIT

DEFAULT_LOGLEVEL = 'WARNING'

CMD_ARGS = [  # list of pairs of (args_tuple, kwargs_dict)
    (['image_dir'], {
        'help': 'path to scan for new images'
    }),
    (['temp_image_dir'], {
        'help': 'path for converted images. must be different from image_dir!',
        'type': str
    }),
    (['--filterconf', '-f'], {
        'help': 'path to filter configuration file',
    })
    ,
    (['--iter', '-n'], {
        'help': 'number of iterations',
        'default': 1,
        'type': int
    }),
    (['--save_steps', '-m'], {
        'help': 'save every n steps',
        'default': 0,
        'type': int
    }),
    (['--scan_inverval_s', '-s'], {
        'help': 'scan interval in s',
        'default': 0.5,
        'type': float
    }),
    (['--display_inverval_s', '-d'], {
        'help': 'display interval in s',
        'default': 1.5,
        'type': float
    }),
    (['--file_pattern', '-p'], {
        'help': 'scan file pattern',
        'default': '^.*\.(jpg|png)$',
        'type': str
    })
]

class Window():
    def __init__(self, queue_in):
        self.queue_in = queue_in
        pyg.init()
        winf = pyg.display.Info()
        self.window_width = winf.current_w // 3
        self.window_height = winf.current_h // 3
        logging.info('WINDOW INIT %dx%d' % (self.window_width, self.window_height))
        self.surface = pyg.display.set_mode((self.window_width, self.window_height), pyg.FULLSCREEN) # pyg.NOFRAME +

        icon_size = 128
        icon_file = 'icon%d.png' % icon_size
        icon_path = os.path.join(os.path.dirname(sys.argv[0]), icon_file)
        icon_image = pyg.image.load(icon_path)
        pyg.display.set_caption("imagedecay")
        pyg.display.set_icon(icon_image)

    def run(self):

        self.running = True
        while self.running:
            try:
                events = pyg.event.get()
            except KeyboardInterrupt:
                self.running = False
                break
            except:
                events = []
            for e in events:
                if e.type == pyg.locals.QUIT:
                    self.running = False
                    break
            #pyg.event.pump()
            try:
                img = self.queue_in.get_nowait()
            except:
                img = None
            if img:
                self.display(img)
        self.running = False
        pyg.display.quit()
        logging.debug('WINDOW QUIT')


    def display(self, imgpath):
        logging.debug(imgpath)
        img = pyg.image.load(imgpath)
        img_width, img_height = img.get_rect().width, img.get_rect().height
        img_uppler_left = int((self.window_width - img_width) / 2), int((self.window_height - img_height) / 2)
        #logging.debug("DISP blit")
        self.surface.blit(img, img_uppler_left)
        #logging.debug("DISP flip")
        pyg.display.flip()
        #logging.debug("DISP OK")


def main(**kwargs):
    image_dir = kwargs['image_dir']
    temp_image_dir = kwargs['temp_image_dir']
    assert(image_dir != temp_image_dir)
    assert(os.path.exists(image_dir))
    assert(os.path.exists(temp_image_dir))

    queue_scan = Queue()
    queue_seq = Queue()
    queue_disp = Queue()

    conf = get_conf(kwargs['filterconf'])


    scanner = Scanner(queue=queue_scan, path=image_dir, interval_s=kwargs['scan_inverval_s'], file_pattern=kwargs['file_pattern'])
    display = Display(queue_in=queue_seq, queue_out=queue_disp, interval_s=kwargs['display_inverval_s'])
    converter = Converter(queue_in=queue_scan, queue_out=queue_seq, path=temp_image_dir, conf=conf, n_iter=kwargs['iter'], save_steps=kwargs['save_steps'])
    window = Window(queue_in=queue_disp)

    display.start()
    converter.start()
    scanner.start()


    try:
        window.run()
    except KeyboardInterrupt:
        pass
    finally:
        scanner.stop()
        converter.stop()
        display.stop()



def on_error(**kwargs):
    pass


def on_interrup(**kwargs):
    pass


def on_finally(**kwargs):
    pass


if __name__ == '__main__':
    # command line > environment variables > config file values > defaults
    ap = configargparse.ArgParser(
        default_config_files=[],     # add config files here
        add_config_file_help=False,  # but dont show help about the syntax
        auto_env_var_prefix=None,    # use environment variables without prefix (None for not using them)
        add_env_var_help=False       # but dont show help about that either
    )
    ap.add('-c', '--config', required=False, is_config_file=True, help='config file path')
    ap.add('--loglevel', '-l', type=str, default=DEFAULT_LOGLEVEL, help='ERROR, WARNING, INFO, or DEBUG')
    # add additional arguments
    for a in CMD_ARGS:
        ap.add(*a[0], **a[1])
    # parse and make a dictionary
    settings = vars(ap.parse_args())
    # reset basic config, set loglevel
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(format='[%(asctime)s %(funcName)s %(levelname)s] %(message)s',
                        level=getattr(logging, settings.get('loglevel').upper()))
    logging.debug('ARGUMENTS:\n' + ap.format_values())


    # main wrapper
    rc = 0
    try:
        main(**settings)
    except KeyboardInterrupt:
        on_interrup(**settings)
        rc = 130
    except Exception as e:  # unhandled Exception
        logging.error(e, exc_info=e)  # show error trace
        on_error(**settings)
        rc = 1
    on_finally(**settings)
    sys.exit(rc)

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
import time
import os

DEFAULT_LOGLEVEL = 'DEBUG'

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



def main(**kwargs):
    image_dir = kwargs['image_dir']
    temp_image_dir = kwargs['temp_image_dir']
    assert(image_dir != temp_image_dir)
    assert(os.path.exists(image_dir))
    assert(os.path.exists(temp_image_dir))

    queue_in = Queue()
    queue_out = Queue()
    conf = get_conf(kwargs['filterconf'])

    scanner = Scanner(queue=queue_in, path=image_dir, interval_s=kwargs['scan_inverval_s'], file_pattern=kwargs['file_pattern'])
    display = Display(queue=queue_out, interval_s=kwargs['display_inverval_s'])
    converter = Converter(queue_in=queue_in, queue_out=queue_out, path=temp_image_dir, conf=conf, n_iter=kwargs['iter'], save_steps=kwargs['save_steps'])
    display.start()
    converter.start()
    scanner.start()

    try:
        time.sleep(10)
    except:
        pass

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
        default_config_files=[],    # add config files here
        add_config_file_help=False, # but dont show help about the syntax
        auto_env_var_prefix=None,   # use environment variables without prefix (None for not using them)
        add_env_var_help=False      # but dont show help about that either
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

    # input output stream as byte stream
    sys.stdout = sys.stdout.detach()
    sys.stdin = sys.stdin.detach()

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

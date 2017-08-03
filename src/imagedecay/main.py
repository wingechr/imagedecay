#!/usr/bin/env python3
# coding=utf-8
"""Main script for the imagedecay package.
"""

import logging
import configargparse
import sys
from imagedecay.readwrite import read, write
from imagedecay.filter import get_conf, apply_filterconf

DEFAULT_LOGLEVEL = 'DEBUG'

CMD_ARGS = [  # list of pairs of (args_tuple, kwargs_dict)
    (['filepath'], {
        'help': 'filepath to image to process'
    }),
    (['--filterconf'], {
        'help': 'path to filter configuration file',
    })
    ,
    (['--iter'], {
        'help': 'number of iterations',
        'default': 1,
        'type': int
    }),
    (['--save_steps'], {
        'help': 'save every n steps',
        'default': 0,
        'type': int
    })
]


def _get_output_filename(filepath, i):
    return '%s.%06d.png' % (filepath, i)


def main(**kwargs):
    # load filter config
    conf = get_conf(kwargs['filterconf'])
    # load image
    im_array, meta = read(kwargs['filepath'])
    # save original
    write(im_array, _get_output_filename(kwargs['filepath'], 0))

    n = kwargs['iter']
    s = kwargs['save_steps']
    for i in range(1, n + 1):
        logging.debug('STEP % 5d' % i)
        # apply filter
        im_array = apply_filterconf(im_array, conf)
        # save
        if i == n or (s and i % s == 0):
            write(im_array, _get_output_filename(kwargs['filepath'], i))


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

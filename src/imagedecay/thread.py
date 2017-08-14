# coding=utf-8
"""Simple stoppable thread."""

from threading import Thread
import logging
import sys

import configargparse

class MyThread(Thread):
    """Simple stoppable thread."""
    def __init__(self):
        super().__init__(target=self.run, daemon=False)
        self.running = False

    def run(self):
        """Main thread. Must check occasionally for self.runing"""
        raise NotImplementedError

    def start(self):
        """Start the thread."""
        self.running = True
        super().start()

    def stop(self):
        """Stop the thread."""
        self.running = False


def main_setup(main_fun, cmd_args, default_loglevel):
    """Prepare arguments and environment for main."""
    # command line > environment variables > config file values > defaults
    argp = configargparse.ArgParser(
        default_config_files=[],  # add config files here
        add_config_file_help=False,  # but dont show help about the syntax
        auto_env_var_prefix=None,  # use environment vars without prefix (None for not using them)
        add_env_var_help=False  # but dont show help about that either
    )
    #ap.add('-c', '--config', required=False, is_config_file=True, help='config file path')
    argp.add('--loglevel', '-l', type=str, default=default_loglevel,
             help='ERROR, WARNING, INFO, or DEBUG')
    # add additional arguments
    for arg in cmd_args:
        argp.add(*arg[0], **arg[1])
    # parse and make a dictionary
    kwargs = vars(argp.parse_args())
    # reset basic config, set loglevel
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(format='[%(asctime)s %(funcName)s %(levelname)s] %(message)s',
                        level=getattr(logging, kwargs.get('loglevel').upper()))
    logging.debug('ARGUMENTS:\n' + argp.format_values())
    # main wrapper
    retcode = 0
    try:
        main_fun(**kwargs)
    except KeyboardInterrupt:
        retcode = 130
    except Exception as err:  # unhandled Exception
        logging.error(err, exc_info=err)  # show error trace
        retcode = 1
    sys.exit(retcode)

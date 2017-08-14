# coding=utf-8
"""Simple stoppable thread."""

from threading import Thread
import logging
import sys
from queue import Queue, Empty

import configargparse
Thread()

class MyThread(Thread):
    """Simple stoppable thread."""
    def __init__(self, daemon=True):
        super().__init__(target=self.run, daemon=daemon)
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


class MyQueue():
    """Synchronized queue"""
    def __init__(self):
        self._queue = Queue()

    def put(self, item):
        """Put item into queue."""
        self._queue.put(item, block=True)

    def _get_next_or_none(self):
        try:
            item = self._queue.get(block=False)
        except Empty as dummy_exc:
            item = None
        return item

    def get_last_nowait(self):
        """Get last item (discard others), but don't wait if empty (return None)"""
        item_next = self._get_next_or_none()
        item = item_next
        while item_next is not None:
            item = item_next
            item_next = self._get_next_or_none()
        return item

    def get_last_wait(self):
        """Get last item (discard others), but wait if empty"""
        item = self.get_last_nowait()
        if not item:
            item = self.get_first_wait(clear_rest=False)
        return item

    def get_first_nowait(self, clear_rest=False):
        """Get first item (discard others optionally), but don't wait if empty (return None)"""
        item = self._get_next_or_none()
        if clear_rest:
            self.get_last_nowait()
        return item

    def get_first_wait(self, clear_rest=False):
        """Get first item (discard others), but wait if empty"""
        item = self._queue.get(block=True)
        if clear_rest:
            self.get_last_nowait()
        return item


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
    kwargs, unrecognized_kwargs = argp.parse_known_args()
    kwargs = vars(kwargs)
    # add unknown:
    for i in range(len(unrecognized_kwargs) // 2):  # always in pairs
        key = unrecognized_kwargs[i * 2].replace('--', '')
        val = float(unrecognized_kwargs[i * 2 + 1])  # must be floats
        kwargs[key] = val
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

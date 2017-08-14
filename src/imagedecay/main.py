# coding=utf-8
"""Main script for the imagedecay package."""

import logging
import os
import time
import sys
from queue import Queue

import configargparse
import pygame as pyg
from pygame import camera
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_RETURN

from imagedecay.filter import get_conf
from imagedecay.scanner import Scanner
from imagedecay.display import Display
from imagedecay.converter import Converter


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
        'help': 'path to filter configuration file'
    }),
    (['--iter', '-n'], {
        'help': 'number of iterations',
        'default': 5,
        'type': int
    }),
    (['--save_steps', '-m'], {
        'help': 'save every n steps',
        'default': 1,
        'type': int
    }),
    (['--scan_interval_s', '-s'], {
        'help': 'scan interval in s',
        'default': 1.0,
        'type': float
    }),
    (['--image_screen_ratio', '-r'], {
        'help': 'maximum imgage size comapred to screen sizes',
        'default': 1.0,
        'type': float
    }),
    (['--display_interval_s', '-d'], {
        'help': 'display interval in s',
        'default': 1.5,
        'type': float
    }),
    (['--file_pattern', '-p'], {
        'help': 'scan file pattern',
        'default': r'^.*\.(jpg|png|jpeg|bmp)$',
        'type': str
    }),
    (['--enable_cam'], {
        'help': 'Enable ENTER to take webcam snapshot (Linux only)',
        'action': 'store_true'
    })
]


class Window():
    """Output screen."""
    def __init__(self, get_next, path, image_screen_ratio=1.0, interval_s=1.0, enable_cam=False):
        self.get_next = get_next
        self.interval_s = interval_s
        self.path = path
        self.enable_cam = enable_cam
        pyg.init()
        winf = pyg.display.Info()
        self.window_width = int(winf.current_w * image_screen_ratio)
        self.window_height = int(winf.current_h * image_screen_ratio)
        logging.info('WINDOW INIT (%d x %d) of max (%d x %d)', self.window_width,
                     self.window_height, winf.current_w, winf.current_h)
        window_size = self.window_width, self.window_height
        self.surface = pyg.display.set_mode(window_size, pyg.FULLSCREEN + pyg.NOFRAME)
        self.last_img = None
        icon_size = 128
        icon_file = 'icon%d.png' % icon_size
        icon_path = os.path.join(os.path.dirname(sys.argv[0]), icon_file)
        icon_image = pyg.image.load(icon_path)
        pyg.display.set_caption("imagedecay")
        pyg.display.set_icon(icon_image)
        pyg.mouse.set_visible(False)
        self.last_update = time.time()
        self.running = False

    def run(self):
        """Start the thread."""
        self.running = True
        while self.running:
            try:
                events = pyg.event.get()
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as err:
                events = []
            for err in events:
                if err.type == QUIT or (err.type == KEYDOWN and err.key == K_ESCAPE):
                    logging.info('USER QUIT')
                    self.running = False
                    break
                elif self.enable_cam and err.type == KEYDOWN and err.key == K_RETURN:
                    self.take_webcam_picture()
            now = time.time()
            if now - self.last_update > self.interval_s:
                img = self.get_next()
                self.last_update = now
                self.display(img)
        pyg.display.quit()
        logging.debug('WINDOW QUIT')

    def display(self, imgpath):
        """Show the image on the screen.
        Args:
            imgpath (str): path to image
        """
        logging.debug('WINDOW SHOW %s', imgpath)
        self.clear()
        if imgpath:
            img = pyg.image.load(imgpath)
            img_width, img_height = img.get_rect().width, img.get_rect().height
            img_left = int((self.window_width - img_width) / 2)
            img_top = int((self.window_height - img_height) / 2)
            img_uppler_left = img_left, img_top
            self.surface.blit(img, img_uppler_left)
        pyg.display.flip()

    def clear(self):
        """Clear the screen."""
        self.surface.fill((0, 0, 0))

    def take_webcam_picture(self):
        """Take a picture with buildin webcam and put it in the input folder."""
        camera.init()
        cam = camera.Camera(pyg.camera.list_cameras()[0])
        cam.start()
        img = cam.get_image()
        cam.stop()
        cam_index = int(time.time() * 1000)
        filepath = os.path.join(self.path, '_campic.%s.png' % cam_index)
        logging.info('CAMPIC: %s', filepath)
        pyg.image.save(img, filepath)
        camera.quit()


def main(**kwargs):
    """Entry point for the main script."""
    image_dir = kwargs['image_dir']
    temp_image_dir = kwargs['temp_image_dir']
    assert image_dir != temp_image_dir
    assert os.path.exists(image_dir)
    assert os.path.exists(temp_image_dir)
    list_index = os.path.join(temp_image_dir, 'index.html')
    queue_scan = Queue()
    queue_seq = Queue()
    conf = get_conf(kwargs['filterconf'])
    display = Display(queue_in=queue_seq)
    window = Window(get_next=display.get_next, path=image_dir,
                    image_screen_ratio=kwargs['image_screen_ratio'],
                    interval_s=kwargs['display_interval_s'], enable_cam=kwargs['enable_cam'])
    max_image_size = (window.window_width, window.window_height)
    scanner = Scanner(queue=queue_scan, path=image_dir, interval_s=kwargs['scan_interval_s'],
                      file_pattern=kwargs['file_pattern'])
    converter = Converter(queue_in=queue_scan, queue_out=queue_seq, path=temp_image_dir,
                          conf=conf, n_iter=kwargs['iter'], save_steps=kwargs['save_steps'],
                          max_image_size=max_image_size, list_index=list_index)
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


if __name__ == '__main__':
    # command line > environment variables > config file values > defaults
    AP = configargparse.ArgParser(
        default_config_files=[],  # add config files here
        add_config_file_help=False,  # but dont show help about the syntax
        auto_env_var_prefix=None,  # use environment vars without prefix (None for not using them)
        add_env_var_help=False  # but dont show help about that either
    )
    #ap.add('-c', '--config', required=False, is_config_file=True, help='config file path')
    AP.add('--loglevel', '-l', type=str, default=DEFAULT_LOGLEVEL,
           help='ERROR, WARNING, INFO, or DEBUG')
    # add additional arguments
    for a in CMD_ARGS:
        AP.add(*a[0], **a[1])
    # parse and make a dictionary
    KWARGS = vars(AP.parse_args())
    # reset basic config, set loglevel
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(format='[%(asctime)s %(funcName)s %(levelname)s] %(message)s',
                        level=getattr(logging, KWARGS.get('loglevel').upper()))
    logging.debug('ARGUMENTS:\n' + AP.format_values())
    # main wrapper
    RC = 0
    try:
        main(**KWARGS)
    except KeyboardInterrupt:
        RC = 130
    except Exception as err:  # unhandled Exception
        logging.error(err, exc_info=err)  # show error trace
        RC = 1
    sys.exit(RC)

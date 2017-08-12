Introduction
============

* This is a small tool to create iterative image effects.
* There is a small (but growing> number of filters implemented at this point.
* Their application and configuration can be set up in a simple json config file.

```bash
usage: main.py [-h] [-c CONFIG] [--loglevel LOGLEVEL]
               [--filterconf FILTERCONF] [--iter ITER]
               [--save_steps SAVE_STEPS] [--scan_inverval_s SCAN_INVERVAL_S]
               [--display_inverval_s DISPLAY_INVERVAL_S]
               [--file_pattern FILE_PATTERN]
               image_dir temp_image_dir

positional arguments:
  image_dir             path to scan for new images
  temp_image_dir        path for converted images. must be different from image_dir!                       

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        config file path
  --loglevel LOGLEVEL, -l LOGLEVEL
                        ERROR, WARNING, INFO, or DEBUG
  --filterconf FILTERCONF, -f FILTERCONF
                        path to filter configuration file
  --iter ITER, -n ITER  number of iterations
  --save_steps SAVE_STEPS, -m SAVE_STEPS
                        save every n steps
  --scan_inverval_s SCAN_INVERVAL_S, -s SCAN_INVERVAL_S
                        scan interval in s
  --display_inverval_s DISPLAY_INVERVAL_S, -d DISPLAY_INVERVAL_S
                        display interval in s
  --file_pattern FILE_PATTERN, -p FILE_PATTERN
                        scan file pattern
```

INSTALL
=======

run ``python3 setup.py install``  in root directory


TEST
====

run ``test.bat`` in folder ``example``


TODO
====

* maybe interrupt conversion sequence if new image arrives?

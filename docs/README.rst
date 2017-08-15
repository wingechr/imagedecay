Introduction
============

-  This is a small tool to create iterative image effects.
-  There is a small (but growing> number of filters implemented at this
   point.
-  Their application and configuration can be set up in a simple json
   config file.

.. code:: bash

    usage: main.py [-h] [--loglevel LOGLEVEL] [--filterconf FILTERCONF]
                   [--iter ITER] [--save_steps SAVE_STEPS]
                   [--scan_interval_s SCAN_INTERVAL_S]
                   [--image_screen_ratio IMAGE_SCREEN_RATIO]
                   [--display_interval_s DISPLAY_INTERVAL_S]
                   [--file_pattern FILE_PATTERN] [--enable_cam]
                   [--output_fmt OUTPUT_FMT]
                   image_dir temp_image_dir

    positional arguments:
      image_dir             path to scan for new images
      temp_image_dir        path for converted images. must be different from
                            image_dir!

    optional arguments:
      -h, --help            show this help message and exit
      --loglevel LOGLEVEL, -l LOGLEVEL
                            ERROR, WARNING, INFO, or DEBUG
      --filterconf FILTERCONF, -f FILTERCONF
                            path to filter configuration file
      --iter ITER, -n ITER  number of iterations
      --save_steps SAVE_STEPS, -m SAVE_STEPS
                            save every n steps
      --scan_interval_s SCAN_INTERVAL_S, -s SCAN_INTERVAL_S
                            scan interval in s
      --image_screen_ratio IMAGE_SCREEN_RATIO, -r IMAGE_SCREEN_RATIO
                            maximum imgage size comapred to screen sizes
      --display_interval_s DISPLAY_INTERVAL_S, -d DISPLAY_INTERVAL_S
                            display interval in s
      --file_pattern FILE_PATTERN, -p FILE_PATTERN
                            scan file pattern
      --enable_cam          Enable ENTER to take webcam snapshot (Linux only)
      --output_fmt OUTPUT_FMT
                            output file format

INSTALL
=======

run ``python3 setup.py install`` in root directory

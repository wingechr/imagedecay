Introduction
============

* This is a small tool to create iterative image effects.
* There is a small (but growing) number of filters implemented at this point.
* Their application and configuration can be set up in a simple json config file.

``python -m imagedecay.main --iter=20 --save_steps=2 --filterconf example.json example.jpg``


* This will read the image ``example.jpg`` and will run 20 times, each time applying all the filters specified in ``example.json``.
* The original and the final image, as well as every 2nd intermmediate will be saved as <original_file_name>.00000x.png

* The config file is a simple json file with a list of filters that are applied at each iteration.
* Each filter has a ``name`` and a number of keyword arguments ``kwargs`` that are specific to that filter
* The number of iterations and how many intermeddiate files will be saved can be specified as command line arguments

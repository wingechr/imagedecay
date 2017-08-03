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

Example
=======

We use this image

![](docs/_static/example/samj.jpg width="80%")
   
and this config file:

```json
[
{
    "name": "noise",
    "kwargs": {
        "min": 0.0,
        "max": 0.1
    }
},
{
    "name": "gaussian",
    "kwargs": {
        "sigma": 0.4
    }
},
{
    "name": "colordepth",
    "kwargs": {
        "n_colors": 5
    }
},
{
    "name": "random_offset",
    "kwargs": {
        "alpha": 0.2,
        "dx": 0.02,
        "dy": 0.03
    }
}
]
```


This will apply 

* a little bit of random noise
* some blurring
* some color reduction
* and some random offset overlay

for each iteration.
Running this a few times renders this nice sequence:


![](docs/_static/example/samj.jpg.000000.png width="40%")


   
![](docs/_static/example/samj.jpg.000001.png width="40%")


   
![](docs/_static/example/samj.jpg.000002.png width="40%")


   
![](docs/_static/example/samj.jpg.000003.png width="40%")


   
![](docs/_static/example/samj.jpg.000004.png width="40%")


   
![](docs/_static/example/samj.jpg.000005.png width="40%")


   
![](docs/_static/example/samj.jpg.000006.png width="40%")


   
![](docs/_static/example/samj.jpg.000007.png width="40%")


   
![](docs/_static/example/samj.jpg.000008.png width="40%")


   
![](docs/_static/example/samj.jpg.000009.png width="40%")


   
![](docs/_static/example/samj.jpg.000010.png width="40%")


   
![](docs/_static/example/samj.jpg.000011.png width="40%")


   
![](docs/_static/example/samj.jpg.000012.png width="40%")


   
![](docs/_static/example/samj.jpg.000013.png width="40%")


   
![](docs/_static/example/samj.jpg.000014.png width="40%")


   
![](docs/_static/example/samj.jpg.000015.png width="40%")


   
![](docs/_static/example/samj.jpg.000016.png width="40%")


   
![](docs/_static/example/samj.jpg.000017.png width="40%")


   
![](docs/_static/example/samj.jpg.000018.png width="40%")


   
![](docs/_static/example/samj.jpg.000019.png width="40%")


   
![](docs/_static/example/samj.jpg.000020.png width="40%")


   


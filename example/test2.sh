#!/usr/bin/env bash

python3 -m imagedecay.converter test.png colorrange --power_0=2.0 --power_1=0.5
python3 -m imagedecay.converter test.png colorrange --power_0=0.5 --power_1=2.0
python3 -m imagedecay.converter test.png colorrange --power_0=2.0 --power_1=0.5 --cmin=0 --cmax=1
python3 -m imagedecay.converter test.png colorrange --power_0=0.5 --power_1=2.0 --cmin=0 --cmax=1
python3 -m imagedecay.converter test.png colorrange --power_0=10 --power_1=0.1 --cmin=0 --cmax=1

python3 -m imagedecay.converter test.png colorrange --power_0=0.1 --power_1=0.1 --cmin=0 --cmax=1


python3 -m imagedecay.converter test.png noise --min=0 --max=1 --gauss_sigma=1.0
python3 -m imagedecay.converter test.png noise --min=0 --max=1 --gauss_sigma=2.0
python3 -m imagedecay.converter test.png noise --min=0 --max=1 --gauss_sigma=5.0
python3 -m imagedecay.converter test.png noise --min=0 --max=1 --gauss_sigma=10.0

python3 -m imagedecay.converter test.png noise --min=0.1 --max=0.5 --gauss_sigma=1.0

python3 -m imagedecay.converter test.png colordepth --n_colors=50
python3 -m imagedecay.converter test.png colordepth --n_colors=20
python3 -m imagedecay.converter test.png colordepth --n_colors=10
python3 -m imagedecay.converter test.png colordepth --n_colors=5
python3 -m imagedecay.converter test.png colordepth --n_colors=1

python3 -m imagedecay.converter test.png random_offset --alpha=0.5 --dx=0.05 --dy=0.01
python3 -m imagedecay.converter test.png random_offset --alpha=0.5 --dx=0.1 --dy=0.05

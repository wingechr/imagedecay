# coding: utf-8
"""Read filter from config file.
"""

import json
import sys
import logging
import numpy as np
import scipy.ndimage.filters
import random


def get_conf(filepath, encoding='utf-8'):
    """
    Args:
        name (str): Name of configuration, ``<name>.json`` must be in ``conf`` directory.
        encoding (str, optional): text encoding of config file.
    Returns:
        filter configuration object.
    """
    if not filepath:
        logging.warning('FILTER No filter.')
        return []
    logging.debug('FILTER Read configuration from: ' + filepath)
    with open(filepath, 'r', encoding=encoding) as f:
        data = json.load(f)
    return data


def _get_filter_by_name(name):
    this = sys.modules[__name__]
    funname = 'filter_%s' % name
    fun = getattr(this, funname)
    return fun


def apply_filterconf(im_array, filterconf):
    for f in filterconf:
        im_array = _apply_filter(im_array, f)
    return im_array


def _apply_filter(im_array, filter):
    filter_fun = _get_filter_by_name(filter['name'])
    filter_kwargs = filter['kwargs']
    logging.debug('FILTER %s: %s' % (filter['name'], filter_kwargs))
    im_array = filter_fun(im_array, **filter_kwargs)
    return im_array


def filter_noise(a, min=0.0, max=1.0, gauss_sigma=0.3, **kwargs):
    rnd = np.random.rand(*a.shape)
    rnd = rnd * 2.0 - 1.0
    rnd = rnd * (max - min) + min * np.sign(rnd)
    if gauss_sigma:
        rnd = filter_gaussian(rnd, sigma=gauss_sigma)
    a = a + rnd
    a = a.clip(0.0, 1.0)  # clip
    return a


def filter_colordepth(a, n_colors, **kwargs):
    a = np.round(a * n_colors) / n_colors
    return a


def filter_gaussian(a, sigma, **kwargs):
    a = scipy.ndimage.filters.gaussian_filter(a, sigma=sigma, mode='nearest')
    return a


def filter_random_offset(a, alpha, dx, dy, **kwargs):
    def shift_img(a, n, axis):
        m = a.shape[axis]
        d1 = 0 if n < 0 else n
        d2 = m - (0 if n > 0 else -n)
        r = (n + m) % m
        a_ = np.roll(a, r, axis=axis)
        slices1 = [slice(0, s) for s in a.shape]
        slices1[axis] = slice(0, d1)
        slices2 = [slice(0, s) for s in a.shape]
        slices2[axis] = slice(d2, m)
        a_[slices1] = 0
        a_[slices2] = 0
        return a_
    dx = round((random.random() * 2.0 - 1.0) * dx * a.shape[0])
    dy = round((random.random() * 2.0 - 1.0) * dy * a.shape[1])
    a_ = shift_img(shift_img(a, dx, 0), dy, 1)
    a = a * (1 - alpha) + a_ * alpha
    return a

def filter_colorrange(a, power_0, power_1, cmin=None, cmax=None, **kwargs):
    a = a ** (power_0 + (power_1 - power_0) * a)
    a_min = np.min(a)
    a_max = np.max(a)
    if cmin is None:
        cmin = a_min
    if cmax is None:
        cmax = a_max
    a = (a - a_min) / (a_max - a_min) * (cmax - cmin) + cmin
    return a


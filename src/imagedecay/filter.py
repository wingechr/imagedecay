# coding: utf-8
"""Read filter from config file."""

import json
import sys
import logging
import random

import numpy as np
import scipy.ndimage.filters


def get_conf(filepath, encoding='utf-8'):
    """Read filter from config file.

    Args:
        filepath (str): Path to config json.
        encoding (str, optional): text encoding of config file.

    Returns:
        filter configuration object.
    """
    if not filepath:
        logging.warning('FILTER No filter.')
        return []
    logging.debug('FILTER Read configuration from: %s', filepath)
    with open(filepath, encoding=encoding) as file:
        data = json.load(file)
    return data


def _get_filter_by_name(name):
    this = sys.modules[__name__]
    funname = 'filter_%s' % name
    fun = getattr(this, funname)
    return fun


def apply_filterconf(im_array, filterconf):
    """Apply the given filter to the image array."""
    for flt in filterconf:
        im_array = _apply_filter(im_array, flt)
    return im_array


def _apply_filter(im_array, filter_conf):
    filter_fun = _get_filter_by_name(filter_conf['name'])
    filter_kwargs = filter_conf['kwargs']
    logging.debug('FILTER %s: %s', filter_conf['name'], filter_kwargs)
    im_array = filter_fun(im_array, **filter_kwargs)
    return im_array


def filter_noise(im_array, cmin=0.0, cmax=1.0, gauss_sigma=1.0, **dummy_kwargs):
    """Apply random noise and optional gaussian blur after that.

    Args:
        im_array (array): image array
        cmin (float): minimum noise, defaults to 0.0
        cmax (float): maximum noise, defaults to 0.0
        gauss_sigma (float): standard deviation for gauss filter.
    """
    rnd = np.random.rand(*im_array.shape)
    rnd = rnd * 2.0 - 1.0
    rnd = rnd * (cmax - cmin) + cmin * np.sign(rnd)
    if gauss_sigma:
        rnd = filter_gaussian(rnd, sigma=gauss_sigma)
    im_array = im_array + rnd
    im_array = im_array.clip(0.0, 1.0)  # clip
    return im_array


def filter_colordepth(im_array, n_colors, **dummy_kwargs):
    """Change the number of available colors per channel.

    Args:
        im_array (array): image array
        n_colors (int): number of colors
    """
    im_array = np.round(im_array * n_colors) / n_colors
    return im_array


def filter_gaussian(im_array, sigma, **dummy_kwargs):
    """Apply gaussian filter (blur).

    Args:
        im_array (array): image array
        sigma (float): standard deviation for gauss filter.
    """
    im_array = scipy.ndimage.filters.gaussian_filter(im_array, sigma=sigma, mode='nearest')
    return im_array


def filter_random_offset(im_array, alpha, max_x, max_y, **dummy_kwargs):
    """Overlay a randomly offset copy with some transparency.

    Args:
        im_array (array): image array
        alpha (float): transparency
        max_x (float): max offset in x in percent of width
        max_y (float): max offset in y in percent of height
    """
    def _shift_img(im_array_src, n_pixels, axis):
        n_max_pixels = im_array_src.shape[axis]
        shift_left = 0 if n_pixels < 0 else n_pixels
        shift_right = n_max_pixels - (0 if n_pixels > 0 else -n_pixels)
        shift = (n_pixels + n_max_pixels) % n_max_pixels
        im_array_trgt = np.roll(im_array_src, shift, axis=axis)
        slices1 = [slice(0, s) for s in im_array_src.shape]
        slices1[axis] = slice(0, shift_left)
        slices2 = [slice(0, s) for s in im_array_src.shape]
        slices2[axis] = slice(shift_right, n_max_pixels)
        im_array_trgt[slices1] = 0
        im_array_trgt[slices2] = 0
        return im_array_trgt
    max_x = round((random.random() * 2.0 - 1.0) * max_x * im_array.shape[0])
    max_y = round((random.random() * 2.0 - 1.0) * max_y * im_array.shape[1])
    im_array_shifted = _shift_img(_shift_img(im_array, max_x, 0), max_y, 1)
    im_array = im_array * (1 - alpha) + im_array_shifted * alpha
    return im_array


def filter_colorrange(im_array, power_0, power_1, cmin=None, cmax=None, **dummy_kwargs):
    """Rescale the color range using a power function.

    Args:
        im_array (array): image array
        power_0 (float): exponential power at value 0.0
        power_1 (float): exponential power at value 1.0
        cmin (float): minimum color value
        cmax (float): maximum color value
    """
    im_array = im_array ** (power_0 + (power_1 - power_0) * im_array)
    a_min = np.min(im_array)
    a_max = np.max(im_array)
    if cmin is None:
        cmin = a_min
    if cmax is None:
        cmax = a_max
    im_array = (im_array - a_min) / (a_max - a_min) * (cmax - cmin) + cmin
    return im_array


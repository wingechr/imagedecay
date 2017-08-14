# coding: utf-8
"""Read/write image files to numpy."""

import logging

import skimage
import skimage.io
import skimage.color
import numpy as np

BG_COLOR_FLOAT = 1.0


def read(filepath):
    """Read image data from file.
    Args:
        filepath (str): path to image file
    Returns:
        image array as float, metadata dict
    """
    logging.debug('READ image data from %s', filepath)
    im_array = skimage.io.imread(filepath)
    im_array = convert_to_float(im_array)
    im_array = remove_alpha(im_array)
    im_array = convert_from_greyscale(im_array)
    im_meta = {
        "filepath": filepath,
        "dtype": str(im_array.dtype),
        "shape": im_array.shape
    }
    logging.debug('READ Image metadata: %s', str(im_meta))

    return im_array, im_meta


def write(im_array, filepath):
    """Write image data to file.
    Args:
        im_array (array): image data as float
        filepath (str): path to image file
    """
    logging.debug('SAVE image data to %s', filepath)
    im_array = convert_to_int(im_array, clip=True)
    skimage.io.imsave(filepath, im_array)


def remove_alpha(im_array, bg_color_float=BG_COLOR_FLOAT):
    """Remove alpha channel, if it exists.
    If number of channels is 2 or 4:
    remove last channel by blending it with the background according to transparency.
    Assumes that array is float.
    Args:
        im_array (array): image data
    Returns:
        image data array
    """
    if 'float' not in str(im_array.dtype):
        raise Exception('dtype must by float')
    n_channels = 1 if len(im_array.shape) == 2 else im_array.shape[2]
    if n_channels not in (2, 4):
        return im_array
    # separate alpha
    alpha = im_array[:, :, (n_channels - 1)]
    im_array = im_array[:, :, :-1]
    # stack alpha:
    alpha = np.stack([alpha] * (n_channels - 1), axis=2)
    background = np.ones(shape=im_array.shape, dtype=np.float) * bg_color_float
    im_array = background * (1.0 - alpha) + im_array * alpha
    return im_array


def convert_from_greyscale(im_array):
    """If image has only one color channel: Convert to RGB."""
    if 'float' not in str(im_array.dtype):
        raise Exception('dtype must by float')
    n_channels = 1 if len(im_array.shape) == 2 else im_array.shape[2]
    if n_channels != 1:
        return im_array
    im_array = skimage.color.grey2rgb(im_array, alpha=None)
    return im_array


def convert_to_float(im_array, clip=False):
    """Convert image data from int to float."""
    if 'int' not in str(im_array.dtype):
        logging.warning('Image does not seem to be int.')
        return im_array
    im_array = im_array.astype(np.float) / 255.0
    if clip:
        im_array = im_array.clip(0.0, 1.0)
    return im_array


def convert_to_int(im_array, clip=False):
    """Convert image data from float to int."""
    if 'float' not in str(im_array.dtype):
        logging.warning('Image does not seem to be float.')
        return im_array
    im_array = (im_array * 255.0).astype(np.uint8)
    if clip:
        im_array = im_array.clip(0, 255)
    return im_array


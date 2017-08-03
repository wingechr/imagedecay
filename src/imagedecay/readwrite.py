# coding: utf-8
"""Read/write image fiels to numpy
"""

import logging
import skimage
import skimage.io
import skimage.color
import numpy as np

BG_COLOR_FLOAT = 1.0

def read(filepath):
    """
    Args:
        filepath (str): path to image file
    Returns:
        image array as float, metadata dict
    """
    logging.debug('Read image data from ' + filepath)

    im_array = skimage.io.imread(filepath)
    im_array = convert_to_float(im_array)
    im_array = remove_alpha(im_array)
    im_array = convert_from_greyscale(im_array)

    im_meta = {
        "filepath": filepath,
        "dtype": str(im_array.dtype),
        "shape": im_array.shape
    }
    logging.debug('Image metadata: ' + str(im_meta))

    return im_array, im_meta


def write(im_array, filepath):
    """
    Args:
        im_array (array): image data as float
        filepath (str): path to image file
    """
    logging.debug('Saving image data to ' + filepath)
    im_array = convert_to_int(im_array, clip=True)
    skimage.io.imsave(filepath, im_array)


def remove_alpha(im_array, bg_color_float=BG_COLOR_FLOAT):
    """
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
        logging.warning('Image does not seem to have transparency.')
        return im_array

    # separate alpha
    alpha = im_array[:, :, (n_channels - 1)]
    im_array = im_array[:, :, :-1]
    # stack alpha:
    alpha = np.stack([alpha] * (n_channels - 1), axis=2)
    bg = np.ones(shape=im_array.shape, dtype=np.float) * bg_color_float
    im_array = bg * (1.0 - alpha) + im_array * alpha

    return im_array


def convert_from_greyscale(im_array):
    if 'float' not in str(im_array.dtype):
        raise Exception('dtype must by float')

    n_channels = 1 if len(im_array.shape) == 2 else im_array.shape[2]
    if n_channels != 1:
        logging.warning('Image does not seem to be greyscale.')
        return im_array

    im_array = skimage.color.grey2rgb(im_array, alpha=None)

    return im_array


def convert_to_float(im_array, clip=False):
    if 'int' not in str(im_array.dtype):
        logging.warning('Image does not seem to be int.')
        return im_array
    im_array = im_array.astype(np.float) / 255.0
    if clip:
        im_array = im_array.clip(0.0, 1.0)
    return im_array


def convert_to_int(im_array, clip=False):
    if 'float' not in str(im_array.dtype):
        logging.warning('Image does not seem to be float.')
        return im_array
    im_array = (im_array * 255.0).astype(np.uint8)
    if clip:
        im_array = im_array.clip(0, 255)
    return im_array


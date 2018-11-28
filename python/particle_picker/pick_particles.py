#!/usr/bin/env python2

# Copyright 2015 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = "Imanol Luengo <imanol.luengo@nottingham.ac.uk>"
__copyright__ = "Copyright (C) 2015 Diamond Light Source Ltd."
__license__ = "Apache License v2.0"
__version__ = "0.1"


import os
import sys
import numpy as np
import h5py as h5
import argparse
import warnings
warnings.filterwarnings("ignore")

# Resize
from skimage.transform import resize

# Denoise
from scipy.ndimage import gaussian_filter
from skimage.restoration import denoise_tv_bregman

# Background substraction
from skimage.filter import rank, threshold_otsu
from skimage.morphology import disk, square
from skimage.util import img_as_uint

# Blob detection
from skimage.measure import label
from scipy.ndimage import binary_fill_holes, center_of_mass
from skimage.morphology import disk, erosion, dilation, opening, closing

from read_mrc import read_rec

# Improved colormap
import cm

import matplotlib as mpl
if 'DISPLAY' in os.environ:
    mpl.use('Qt4Agg')
else:
    mpl.use('Agg')
from matplotlib import pyplot as plt
from ruler import InteractiveWindow

###############################################################
# [DEFAULTS] CONFIGURABLE PARAMETERS
###############################################################

defaults = {
    'path': 'data.nxs',
    'dataset': 'entry/result/data',
    'show': 0,
    'coords': True,
    'output': None,

    'resize': 1000,

    'denoise': 1,
    'weight': 7.,
    'tv_max_iter': 100,
    'tv_eps': 1e-4,

    'radius': np.nan,
    'background': 'median',
}

###############################################################
# READ PARAMETERS
###############################################################


def load_params(params):
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=str, default=params['path'],
                        help="File path")
    parser.add_argument("-d", "--dataset", type=str, default=params['dataset'],
                        help="Dataset containing the data (default: \
                              'entry/result/data')")
    parser.add_argument("-n", "--denoise", type=int, default=params['denoise'],
                        help="Denoising method (0:None, 1:Gaussian filter," +
                             " 2: Anisotropic Total Variation). (default: 1)")
    parser.add_argument("-w", "--weight", type=float, default=params['weight'],
                        help="Strength of the denoising filter (default: 7)")
    parser.add_argument("-r", "--radius", type=float, default=params['radius'],
                        help="Particle radius (in pixels). If not given, a user\
                              interface will be prompt to manually draw the \
                              diameter.")
    parser.add_argument("-b", "--background", default=params['background'],
                        help="Background substraction method \
                              (mean|median|maximum|mode)")
    parser.add_argument("-s", "--resize", type=str, default=params['resize'],
                        help="Resize longest dimension to given size \
                              (default: 1000)")
    parser.add_argument("-v", "--show", type=int, default=params['show'],
                        help="Plot intermediate steps with different values. \
                              The higher the value the more outputs are shown.\
                              1: Show final result. 2: Important plots. \
                              >2: Show all intermediate steps.")
    parser.add_argument("-c", "--coords", type=int, default=params['coords'],
                        help="Output final coordinates (default: True)")
    parser.add_argument("-o", "--output", type=str, default=params['output'],
                        help="Existing path to output results as PNG images.")

    args = parser.parse_args()
    return args


###############################################################
# LOAD DATA
###############################################################


def load_hdf5_data(path, dataset, show=0):
    data = None

    if path.endswith('.mrc'):
        try:
            data = np.squeeze(read_rec(path)[1])
        except:
            print("Error loading file '%s'" % path)
            sys.exit(1)
    else:
        with h5.File(path, 'r') as f:
            try:
                data = np.squeeze(f[dataset][:])
            except:
                print("Error: dataset '%s' not found" % dataset)
                sys.exit(1)

    if show > 2:
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.imshow(data, 'optiona')
        plt.title('Image')
        plt.show()

    return data


###############################################################
# RESIZE AND RESCALE DATA
###############################################################


def preprocess_data(data, newsize, show=0):
    old_shape = np.array(data.shape, float)
    if old_shape[0] > old_shape[1]:
        new_width = old_shape[0] * float(newsize) / old_shape[1]
        new_shape = np.array([newsize, new_width], float)
    else:
        new_height = old_shape[1] * float(newsize) / old_shape[0]
        new_shape = np.array([new_height, newsize], float)

    resized = resize(data, new_shape)
    resized -= data.min()
    resized /= data.max()

    if show > 3:
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.imshow(resized, 'optiona')
        plt.title('Resized Image')
        plt.show()

    return resized, old_shape, new_shape


###############################################################
# EXTRACT RADIUS
###############################################################


def get_radius(data, radius, old_shape, new_shape):
    if np.isnan(radius):
        if 'DISPLAY' not in os.environ:
            print("ERROR: No display found, -r or --radius is required.")
            sys.exit(1)
        distance = InteractiveWindow().draw_line(data)
        radius = distance//2
        print("Radius used is %i" % (radius * np.max(old_shape / new_shape)))
    else:
        radius /= np.max(old_shape / new_shape)

    return radius


###############################################################
# DENOISE DATA
###############################################################


def denoise(data, weight, method=1, eps=1e-4, max_iter=100, show=0):
    if method == 1:
        denoised = gaussian_filter(resized, args.weight)
    elif method == 2:
        denoised = denoise_tv_bregman(data, weight, eps=eps, max_iter=max_iter,
                                      isotropic=False)

    if method != 0 and show > 3:
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.imshow(denoised, 'optiona')
        plt.title('Denoised')
        plt.show()

    return denoised


###############################################################
# BACKGROUND SUBSTRACTION
###############################################################


def substract_background(data, radius, background='mean', show=0):
    dmin, dmax = data.min(), data.max()
    tmp = ((data - dmin) / (dmax - dmin) * 255).astype(np.uint8)
    lforeground = rank.minimum(tmp, disk(radius//2))

    if background == 'mean':
        lbackground = rank.mean(lforeground, disk(radius*4)).astype(int)
    elif background == 'median':
        lbackground = rank.median(lforeground, disk(radius*4)).astype(int)
    elif background == 'maximum':
        lbackground = rank.maximum(lforeground, disk(radius*4)).astype(int)
    else:
        lbackground = rank.modal(lforeground, disk(radius*4)).astype(int)

    rdata = (lforeground - lbackground)

    if show > 2:
        fig, axes = plt.subplots(ncols=3, nrows=1, figsize=(30, 10))
        for ax, im, title in zip(axes, [lforeground, lbackground, rdata],
                                 ['Foreground', 'Background', 'Substraction']):
            ax.imshow(im, 'optiona')
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(title)
        plt.show()

    return rdata


###############################################################
# BLOB EXTRACTION
###############################################################


def detect_blobs(data, radius, show=0):
    otsu = threshold_otsu(data)
    result = data <= otsu

    labels = label(result)
    sizes = np.bincount(labels.flatten())

    min_size = (radius * 0.8)**2 * np.pi  # circle area

    segments = np.zeros_like(sizes)
    segments[sizes > min_size] = 1
    segments[np.argmax(sizes)] = 0

    blob_image = segments[labels]

    if show > 2:
        fig, axes = plt.subplots(ncols=3, nrows=1, figsize=(30, 10))
        for ax, img in zip(axes, [result, data, blob_image]):
            ax.imshow(img, 'optiona')
            ax.set_xticks([])
            ax.set_yticks([])
        plt.show()

    return blob_image


###############################################################
# BLOB FILTERING
###############################################################


def detect_particles(data, radius, return_coords=True, show=0):
    filled = binary_fill_holes(data)
    eroded = erosion(filled, disk(radius//2))

    if show > 3:
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.imshow(eroded)
        ax.set_title('Eroded')
        plt.show()

    labels = label(eroded)
    sizes = np.bincount(labels.flatten())

    min_size = (radius * 0.3)**2 * np.pi
    segments = np.zeros(sizes.shape, int)
    segments[sizes > min_size] = np.arange(sizes.shape[0])[sizes > min_size]
    segments[np.argmax(sizes)] = -1

    total = (segments > 0).sum()

    if return_coords:
        final = segments[labels]
        components = np.where(segments != -1)[0]
        coords = np.array(center_of_mass(final != -1, final+1, components+1))
        mask = np.isnan(coords[:, 0]) | np.isnan(coords[:, 1])
        coords = coords[~mask]
        return total, coords

    return total


###############################################################
# RESCALE COORDINATES TO ITS ORIGINAL IMAGE SIZE
###############################################################


def rescale_coordinates(coords, old_shape, new_shape):
    new_coords = coords * (old_shape/new_shape)
    new_coords = new_coords.astype(int)
    return new_coords


###############################################################
# SAVE RESULTS
###############################################################


def proccess_results(data, denoised, coords, coords2, show=0, savepath=None,
                     basename=''):
    save = savepath is not None
    if show > 0 or save:
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.imshow(data, 'gray')
        ys, xs = coords[:, 0], coords[:, 1]
        ax.plot(xs, ys, 'ro')
        plt.axis('image')
        if show > 0:
            plt.show()
        else:
            plt.draw()
        if save:
            plt.xticks([])
            plt.yticks([])
            fig.savefig(os.path.join(savepath, basename + '_results_raw.png'),
                        bbox_inches='tight', pad_inches=0)

    if show > 1 or save:
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.imshow(denoised, 'gray')
        ys, xs = coords2[:, 0], coords2[:, 1]
        ax.plot(xs, ys, 'ro')
        plt.axis('image')
        if show > 1:
            plt.show()
        else:
            plt.draw()
        if save:
            plt.xticks([])
            plt.yticks([])
            fig.savefig(os.path.join(savepath, basename +
                        '_results_denoised.png'), bbox_inches='tight',
                        pad_inches=0)


###############################################################
# MAIN METHOD
###############################################################


if __name__ == '__main__':
    args = load_params(defaults)
    data = load_hdf5_data(args.data, args.dataset, show=args.show)
    resized, old_shape, new_shape = preprocess_data(data, args.resize)
    radius = get_radius(resized, args.radius, old_shape, new_shape)
    denoised = denoise(resized, args.weight, method=args.denoise,
                       show=args.show)
    enhanced = substract_background(denoised, radius,
                                    background=args.background, show=args.show)
    blobs = detect_blobs(enhanced, radius, show=args.show)

    if args.coords:
        basename = os.path.splitext(os.path.basename(args.data))[0]
        n_particles, particles = detect_particles(blobs, radius,
                                                  return_coords=True,
                                                  show=args.show)
        coordinates = rescale_coordinates(particles, old_shape, new_shape)
        proccess_results(data, denoised, coordinates, particles,
                         show=args.show, savepath=args.output,
                         basename=basename)
        print(n_particles)
        if args.output is not None:
            f = open(os.path.join(args.output, basename + '_points.csv'), 'w')
        for coord in coordinates:
            if args.output is not None:
                f.write('%d,%d\n' % (coord[0], coord[1]))
            print("%d %d" % (coord[0], coord[1]))
        if args.output is not None:
            f.close()
    else:
        n_particles = detect_particles(blobs, radius, coords=False)
        print(n_particles)

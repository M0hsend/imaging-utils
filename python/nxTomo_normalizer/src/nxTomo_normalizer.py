'''
 Copyright 2013 Diamond Light Source Ltd.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

@author: mark.basham@diamond.ac.uk
'''

from operator import itemgetter
from itertools import groupby

import numpy as np
import h5py


class MetaManager():

    def __init__(self, hdf_file_name,
            key_entry_location='/entry1/tomo_entry/instrument/detector/image_key'):
        self._file_handle = h5py.File(hdf_file_name, 'r')
        self._key_entry_location = key_entry_location
        self.build_lists()

    def get_keys(self):
        return self._file_handle[self._key_entry_location][:]

    def group_sequential(self, key_data):
        result = []
        for k, g in groupby(enumerate(key_data), lambda(i, x): i - x):
            result.append(np.array(map(itemgetter(1), g)))
        return result

    def build_lists(self, dark_tag=2, flat_tag=1, projection_tag=0):
        keys = self.get_keys()
        p = np.arange(keys.shape[0])
        self._dark_positions = self.group_sequential(p[keys == dark_tag])
        self._flat_positions = self.group_sequential(p[keys == flat_tag])
        self._projection_positions = \
            self.group_sequential(p[keys == projection_tag])

    def get_bounding_groups(self, group, bounding_group_list):
        if len(bounding_group_list) <= 1:
            return (bounding_group_list[0], bounding_group_list[0],
                    np.zeros(len(group)))
        for i in range(len(bounding_group_list)):
            if group[0] < bounding_group_list[i].min():
                div = float(bounding_group_list[i].min() - bounding_group_list[i - 1].max())
                start_proportion = float(group[0] - bounding_group_list[i - 1].max()) / div
                end_proportion = float(group[-1] - bounding_group_list[i - 1].max()) / div
                return (bounding_group_list[i - 1], bounding_group_list[i],
                        np.linspace(start_proportion, end_proportion, len(group)))

    def get_projection_positions(self):
        return np.concatenate(self._projection_positions)

    def get_flat_positions(self):
        return np.concatenate(self._flat_positions)

    def get_dark_positions(self):
        return np.concatenate(self._dark_positions)

    def get_grouped_positions(self, positions, groups):
        result = []
        for group in groups:
            intersect = np.intersect1d(positions, group)
            if len(intersect) > 0:
                result.append(intersect)
        return result

    def get_grouped_projection_positions(self, positions):
        return self.get_grouped_positions(positions, self._projection_positions)


class DataManager():

    def __init__(self, hdf_file_name, 
                 data_entry_location='/entry1/tomo_entry/data/data'):
        self._file_handle = h5py.File(hdf_file_name, 'r')
        self._data_entry_location = data_entry_location

    def get_frames(self, frame_list):
        result = self._file_handle[self._data_entry_location][frame_list, :, :]
        if len(result.shape) == 2:
            result.shape = (1, result.shape[0], result.shape[1])
        return result

    def get_sino_frames(self, frame_list, sino_start, sino_end):
        result = self._file_handle[self._data_entry_location][frame_list, sino_start:sino_end, :]
        if len(result.shape) == 2:
            result.shape = (1, result.shape[0], result.shape[1])
        return result


def extract_projections(hdf_file_name, start_projection, end_projection):
    meta = MetaManager(hdf_file_name)
    data = DataManager(hdf_file_name)
    return data.get_frames(meta.get_projection_positions()[start_projection:end_projection])


def extract_flats(hdf_file_name, start_flat, end_flat):
    meta = MetaManager(hdf_file_name)
    data = DataManager(hdf_file_name)
    return data.get_frames(meta.get_flat_positions()[start_flat:end_flat])


def extract_darks(hdf_file_name, start_dark, end_dark):
    meta = MetaManager(hdf_file_name)
    data = DataManager(hdf_file_name)
    return data.get_frames(meta.get_dark_positions()[start_dark:end_dark])


def extract_flat_corrected_projections(hdf_file_name, start_projection, end_projection):
    meta = MetaManager(hdf_file_name)
    data = DataManager(hdf_file_name)
    positions = meta.get_projection_positions()[start_projection:end_projection]
    print "positions", positions
    groups = meta.get_grouped_projection_positions(positions)
    print "groups", groups
    frames = []
    for group in groups:
        # get dark and flat data
        darks = meta.get_bounding_groups(group, meta._dark_positions)
        d0 = data.get_frames(darks[0]).mean(0)
        d1 = data.get_frames(darks[1]).mean(0)
        flats = meta.get_bounding_groups(group, meta._flat_positions)
        f0 = data.get_frames(flats[0]).mean(0)
        f1 = data.get_frames(flats[1]).mean(0)
        # get the group data
        group_data = data.get_frames(group)
        for i in range(group_data.shape[0]):
            flat = (f0 * (1.0 - flats[2][i])) + (f1 * (flats[2][i]))
            dark = (d0 * (1.0 - darks[2][i])) + (d1 * (darks[2][i]))
            corrected = ((group_data[i:i + 1, :, :] - dark) / (flat - dark))
            frames.append(corrected)
    return np.vstack(frames)


def extract_flat_corrected_sinograms(hdf_file_name, start_sinogram, end_sinogram):
    meta = MetaManager(hdf_file_name)
    data = DataManager(hdf_file_name)
    positions = meta.get_projection_positions()
    print "positions", positions
    groups = meta.get_grouped_projection_positions(positions)
    print "groups", groups
    frames = []
    for group in groups:
        # get dark and flat data
        darks = meta.get_bounding_groups(group, meta._dark_positions)
        d0 = data.get_sino_frames(darks[0], start_sinogram, end_sinogram).mean(0)
        d1 = data.get_sino_frames(darks[1], start_sinogram, end_sinogram).mean(0)
        flats = meta.get_bounding_groups(group, meta._flat_positions)
        f0 = data.get_sino_frames(flats[0], start_sinogram, end_sinogram).mean(0)
        f1 = data.get_sino_frames(flats[1], start_sinogram, end_sinogram).mean(0)
        # get the group data
        group_data = data.get_sino_frames(group, start_sinogram, end_sinogram)
        for i in range(group_data.shape[0]):
            flat = (f0 * (1.0 - flats[2][i])) + (f1 * (flats[2][i]))
            dark = (d0 * (1.0 - darks[2][i])) + (d1 * (darks[2][i]))
            corrected = ((group_data[i:i + 1, :, :] - dark) / (flat - dark))
            frames.append(corrected)
    return np.vstack(frames)

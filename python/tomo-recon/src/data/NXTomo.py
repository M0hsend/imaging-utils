'''
Created on 2 Jun 2014

@author: ssg37927
'''

import logging
import numpy as np
import h5py


class NXtomo(object):
    '''
    classdocs
    '''

    def __init__(self, filename):
        '''
        Constructor
        '''
        self.file = h5py.File(filename, 'r')
        self.nxtomo = self.get_nxtomo_entry()
        self._image_key = self.nxtomo['instrument/detector/image_key'][...]
        self.darks = self.nxtomo['instrument/detector/data'][self._image_key == 2, :, :]
        self.flats = self.nxtomo['instrument/detector/data'][self._image_key == 1, :, :]
        self.rotation_angle = self.nxtomo['sample/rotation_angle'][self._image_key == 0]
        self.projection_frames = np.arange(len(self._image_key))[self._image_key == 0]

    def get_nxtomo_entry(self):
        for key in self.file.keys():
            if 'NX_class' in self.file[key].attrs.keys():
                if self.file[key].attrs['NX_class'] in ['NXentry', 'NXsubentry']:
                    if 'definition' in self.file[key].keys():
                        if self.file[key]['definition'][0] == 'NXtomo':
                            return self.file[key]
                    for key2 in self.file[key].keys():
                        if 'NX_class' in self.file[key][key2].attrs.keys():
                            if self.file[key][key2].attrs['NX_class'] in ['NXentry', 'NXsubentry']:
                                if 'definition' in self.file[key][key2].keys():
                                    if self.file[key][key2]['definition'][0] == 'NXtomo':
                                        return self.file[key][key2]
        raise KeyError('NXTomo entry not found in this file')

    def get_projections(self, projection_list):
        frame_list = self.projection_frames[projection_list]
        return self.nxtomo['instrument/detector/data'][frame_list, :, :]

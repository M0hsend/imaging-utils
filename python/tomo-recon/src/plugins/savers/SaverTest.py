import logging
from Saver import Saver
import h5py
import numpy as np


class SaverTest(Saver):

    def __init__(self):
        super(Saver)

    def requires(self, meta):
        num_sections = 5
        section_length = (meta.get_number_of_frames() / num_sections)
        if (section_length * num_sections) < meta.get_number_of_frames():
            section_length += 1
        pro_frames = np.arange(meta.get_number_of_frames())
        frame_batch = []

        for i in range(num_sections):
            framelist = pro_frames[:section_length]
            frame_batch.append(framelist)
            pro_frames = pro_frames[section_length:]

        return frame_batch

    def setup(self, filename, meta):
        self._file = h5py.File(filename, 'w')
        self._dataset = self._file.create_dataset('test', meta.get_data_shape(), np.double)

    def save(self, data, frames, frame_list):
        self._dataset[frame_list, :, :] = frames

    def teardown(self, data):
        self._file.close()

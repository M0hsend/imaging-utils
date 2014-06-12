'''
Created on 20 May 2014

@author: ssg37927
'''
import unittest
import utils
import inspect
import os

import numpy as np

from data import NXTomo
import logging


class GeneralTestCase(unittest.TestCase):
    def __init__(self, methodName, param1):
        super(GeneralTestCase, self).__init__(methodName)

        self.param1 = param1

    def runTest(self):
        data = NXTomo.NXtomo(get_test_data_path())

        filt = utils.load_filter_plugin(self.param1)
        filt.setup(data)

        num_sections = 5
        section_length = (len(data.projection_frames) / num_sections)
        if (section_length * num_sections) < len(data.projection_frames):
            section_length += 1
        pro_frames = np.arange(data.projection_frames.shape[0])
        frame_batch = []

        for i in range(num_sections):
            framelist = pro_frames[:section_length]
            frame_batch.append(filt.requires(framelist))
            pro_frames = pro_frames[section_length:]

        for framelist in frame_batch:
            frames = data.get_projections(framelist)
            filt.process(data, frames)

        filt.teardown(data)


def load_tests(filter_names):
    test_cases = unittest.TestSuite()
    for filter_name in filter_names:
        test_cases.addTest(GeneralTestCase('runTest', filter_name))
    return test_cases


def get_test_data_path():
    path = inspect.stack()[0][1]
    return '/'.join(os.path.split(path)[0].split(os.sep)[:-2] + ['test_data', '24737.nxs'])


def run_tests(filter_name_list):
    suite = load_tests(filter_name_list)
    unittest.TextTestRunner(verbosity=2).run(suite)
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
import tempfile


class LoaderTestCase(unittest.TestCase):
    def __init__(self, methodName, param1):
        super(LoaderTestCase, self).__init__(methodName)

        self.param1 = param1

    def runTest(self):
        data_filename = get_test_data_path()

        loader = utils.load_loader_plugin(self.param1)
        loader.setup(data_filename)

        meta = loader.load_metadata()

        num_sections = 5
        section_length = (meta.get_number_of_frames() / num_sections)
        if (section_length * num_sections) < meta.get_number_of_frames():
            section_length += 1
        pro_frames = np.arange(meta.get_number_of_frames())

        for i in range(num_sections):
            framelist = pro_frames[:section_length]
            loader.load_frames(framelist)
            pro_frames = pro_frames[section_length:]

        loader.teardown()


class FilterTestCase(unittest.TestCase):
    def __init__(self, methodName, param1):
        super(FilterTestCase, self).__init__(methodName)

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


class SaverTestCase(unittest.TestCase):
    def __init__(self, methodName, param1):
        super(SaverTestCase, self).__init__(methodName)

        self.param1 = param1

    def runTest(self):
        data = NXTomo.NXtomo(get_test_data_path())

        saver = utils.load_saver_plugin(self.param1)
        tempfilename = tempfile.mktemp('.nxs')
        logging.debug('Temporary file being written : %s' % tempfilename)
        saver.setup(tempfilename, data)

        frame_batch = saver.requires(data)

        for framelist in frame_batch:
            frames = data.get_projections(framelist)
            saver.save(data, frames, framelist)

        saver.teardown(data)


def add_filter_tests(test_suite, filter_names):
    for name in filter_names:
        test_suite.addTest(FilterTestCase('runTest', name))
    return


def add_loader_tests(test_suite, loader_names):
    for name in loader_names:
        test_suite.addTest(LoaderTestCase('runTest', name))
    return


def add_saver_tests(test_suite, saver_names):
    for name in saver_names:
        test_suite.addTest(SaverTestCase('runTest', name))
    return


def get_test_data_path():
    path = inspect.stack()[0][1]
    return '/'.join(os.path.split(path)[0].split(os.sep)[:-2] + ['test_data', '24737.nxs'])


def run_tests(loader_name_list=[], filter_name_list=[], saver_name_list=[]):
    suite = unittest.TestSuite()
    add_loader_tests(suite, loader_name_list)
    add_filter_tests(suite, filter_name_list)
    add_saver_tests(suite, saver_name_list)
    unittest.TextTestRunner(verbosity=2).run(suite)

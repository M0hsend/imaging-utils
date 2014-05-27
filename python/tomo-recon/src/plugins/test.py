'''
Created on 20 May 2014

@author: ssg37927
'''
import unittest
import utils

class GeneralTestCase(unittest.TestCase):
    def __init__(self, methodName, param1):
        super(GeneralTestCase, self).__init__(methodName)

        self.param1 = param1

    def runTest(self):
        filt = utils.load_filter_plugin(self.param1)
        self.assertEqual("preproceesing filter test", filt.preprocess())
        self.assertEqual("processing filter test", filt.process())
        self.assertEqual("postprocessing filter test", filt.postprocess())


def load_tests(filter_names):
    test_cases = unittest.TestSuite()
    for filter_name in filter_names:
        test_cases.addTest(GeneralTestCase('runTest', filter_name))
    return test_cases

def run_tests(filter_name_list):
    suite = load_tests(filter_name_list)
    unittest.TextTestRunner(verbosity=2).run(suite)
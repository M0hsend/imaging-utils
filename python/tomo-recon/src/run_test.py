'''
Created on 20 May 2014

@author: ssg37927
'''
import logging
logging.basicConfig(level=logging.DEBUG)

import plugins.test as pt

pt.run_tests(filter_name_list=["FilterTest",
                               #"FilterTestPlot",
                               "Median3x3Filter"],
             loader_name_list=["LoaderTest",
                               "LoaderTestPlot"])

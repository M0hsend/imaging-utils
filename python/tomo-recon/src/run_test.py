'''
Created on 20 May 2014

@author: ssg37927
'''
import logging
logging.basicConfig(level=logging.DEBUG)

import plugins.test as pt

pt.run_tests(loader_name_list=[
                               "LoaderTest",
                               #"LoaderTestPlot",
                               ],
             filter_name_list=[
                               "FilterTest",
                               #"FilterTestPlot",
                               "Median3x3Filter",
                               ],
             saver_name_list=[
                              "SaverTest",
                              ])

'''
Created on 28 Jan 2014

@author: ssg37927
'''
import inspect
import os
import sys

class plugin_manager(object):
    
    def __init__(self):
        self.dir = os.path.dirname(inspect.getfile(self.__class__))

    def get_loader_plugin(self, plugin_name):
        # Add to the path
        sys.path.append(os.path.join(self.dir, 'loader'))
        mod =  __import__(plugin_name)
        return globals()[plugin_name](1)
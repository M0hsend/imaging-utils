'''
Created on 28 Jan 2014

@author: ssg37927
'''
from loader_api import Loader
import inspect

class SimpleLoader(Loader):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    def load(self):
        print(inspect.getfile(self.__class__))
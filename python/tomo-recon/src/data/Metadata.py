'''
Created on 16 Jun 2014

@author: ssg37927
'''

import logging


class TomoMetadata(object):

    def __init__(self, params):
        pass

    def get_dark_frames(self):
        logging.error("get_dark_frames needs to be implemented")
        raise NotImplementedError("get_dark_frames needs to be implemented")

    def get_flat_frames(self):
        logging.error("get_dark_frames needs to be implemented")
        raise NotImplementedError("get_dark_frames needs to be implemented")

    def get_angles(self):
        logging.error("get_dark_frames needs to be implemented")
        raise NotImplementedError("get_dark_frames needs to be implemented")

    def get_number_of_frames(self):
        logging.error("get_number_of_frames needs to be implemented")
        raise NotImplementedError("get_number_of_frames needs to be implemented")

    def get_data_shape(self):
        logging.error("get_data_shape needs to be implemented")
        raise NotImplementedError("get_data_shape needs to be implemented")
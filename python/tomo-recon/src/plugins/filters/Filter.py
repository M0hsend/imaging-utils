import logging


class Filter(object):

    def __init__(self):
        super(self)

    def requires(self, frame_list):
        logging.error("Requires needs to be implemented")
        raise NotImplementedError("requires needs to be implemented")

    def setup(self, data):
        logging.error("Setup needs to be implemented")
        raise NotImplementedError("Setup needs to be implemented")

    def process(self, data, frames):
        logging.error("process needs to be implemented")
        raise NotImplementedError("process needs to be implemented")

    def teardown(self, data):
        logging.error("process needs to be implemented")
        raise NotImplementedError("process needs to be implemented")

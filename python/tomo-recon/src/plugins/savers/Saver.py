import logging


class Saver(object):

    def __init__(self):
        super(self)

    def requires(self, data):
        logging.error("Requires needs to be implemented")
        raise NotImplementedError("requires needs to be implemented")

    def setup(self, filename):
        logging.error("Setup needs to be implemented")
        raise NotImplementedError("Setup needs to be implemented")

    def save(self, data, frames, frame_list):
        logging.error("process needs to be implemented")
        raise NotImplementedError("process needs to be implemented")

    def teardown(self, data):
        logging.error("process needs to be implemented")
        raise NotImplementedError("process needs to be implemented")

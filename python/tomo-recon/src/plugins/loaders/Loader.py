import logging


class Loader(object):

    def __init__(self):
        super(self)

    def setup(self, filename):
        logging.error("Setup needs to be implemented")
        raise NotImplementedError("Setup needs to be implemented")

    def load_metadata(self):
        logging.error("load_metadata needs to be implemented")
        raise NotImplementedError("load_metadata needs to be implemented")

    def load_frames(self, frame_list):
        logging.error("load_frames needs to be implemented")
        raise NotImplementedError("load_frames needs to be implemented")

    def teardown(self):
        logging.error("process needs to be implemented")
        raise NotImplementedError("process needs to be implemented")

import logging
from Filter import Filter


class FilterTest(Filter):

    def __init__(self):
        super(Filter, self)

    def requires(self, frame_list):
        logging.debug("Running requires")
        return frame_list

    def setup(self, data):
        logging.debug("Running Setup")
        return

    def process(self, data, frame):
        logging.debug("Running Process")
        return

    def teardown(self, data):
        logging.debug("Running Teardown")
        return

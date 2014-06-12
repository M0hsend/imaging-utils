import logging
import time
from Filter import Filter
import scisoftpy as dnp


class FilterTestPlot(Filter):

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
        for i in range(frame.shape[0]):
            dnp.plot.image(frame[i, :, :])
            time.sleep(0.1)
        return

    def teardown(self, data):
        logging.debug("Running Teardown")
        return

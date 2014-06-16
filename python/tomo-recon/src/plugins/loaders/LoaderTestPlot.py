import logging
from Loader import Loader

from data.NXTomo import NXtomo
import scisoftpy as dnp
import time


class LoaderTestPlot(Loader):

    def __init__(self):
        super(Loader, self)

    def setup(self, filename):
        logging.debug("Running Setup")
        self._localdata = NXtomo(filename)
        return

    def load_metadata(self):
        logging.debug("Running Load_metadata")
        return self._localdata

    def load_frames(self, frame_list):
        logging.debug("Running Load_Frames")
        frames = self._localdata.get_projections(frame_list)
        for i in range(frames.shape[0]):
            dnp.plot.image(frames[i, :, :])
            time.sleep(0.1)
        return frames

    def teardown(self):
        logging.debug("Running Teardown")
        return

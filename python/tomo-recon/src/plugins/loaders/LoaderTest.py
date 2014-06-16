import logging
from Loader import Loader

from data.NXTomo import NXtomo


class LoaderTest(Loader):

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
        return frames

    def teardown(self):
        logging.debug("Running Teardown")
        return

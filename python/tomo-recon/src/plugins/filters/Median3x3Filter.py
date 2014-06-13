import logging
import numpy as np
from Filter import Filter


class Median3x3Filter(Filter):

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
        result = np.empty_like(frame)
        for i in range(frame.shape[0]):
            stack = []
            stack.append(frame[i, :, :])
            stack.append(np.roll(stack[0], 1, axis=0))
            stack.append(np.roll(stack[0], -1, axis=0))
            stack.append(np.roll(stack[0], 1, axis=1))
            stack.append(np.roll(stack[0], -1, axis=1))
            stack.append(np.roll(stack[1], 1, axis=1))
            stack.append(np.roll(stack[1], -1, axis=1))
            stack.append(np.roll(stack[2], 1, axis=1))
            stack.append(np.roll(stack[2], -1, axis=1))
            dstack = np.dstack(stack)
            result[i, :, :] = np.mean(dstack, axis=2)

        return result

    def teardown(self, data):
        logging.debug("Running Teardown")
        return


# Copyright 2015 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = "Imanol Luengo <imanol.luengo@nottingham.ac.uk>"
__copyright__ = "Copyright (C) 2015 Diamond Light Source Ltd."
__license__ = "Apache License v2.0"
__version__ = "0.1"


import cm
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt

mpl.interactive(False)


class InteractiveWindow(object):

    def draw_line(self, im):
        plt.ioff()
        self.pressed = False
        self.fig, self.ax = plt.subplots(1, 1, figsize=(10, 10))
        self.ax.imshow(im, 'optiona')
        self.ax.set_title('DRAW LINE - DIAMETER')
        self.fig.canvas.mpl_connect('button_press_event', self.onmousepress)
        self.fig.canvas.mpl_connect('button_release_event', self.onmouserelease)
        self.fig.canvas.mpl_connect('motion_notify_event', self.onmousemove)
        plt.tight_layout()
        plt.show()
        return self.distance

    def onmousepress(self, event):
        self.init = np.array([event.xdata, event.ydata], float)
        self.line = self.ax.plot([event.xdata], [event.ydata])[0]
        self.ax.axis('image')
        self.xs = list(self.line.get_xdata())
        self.ys = list(self.line.get_ydata())
        self.pressed = True

    def onmousemove(self, event):
        if not self.pressed:
            return
        if event.inaxes != self.ax:
            return

        xs = self.xs + [event.xdata]
        ys = self.ys + [event.ydata]

        self.line.set_data(xs, ys)
        self.line.figure.canvas.draw_idle()

    def onmouserelease(self, event):
        self.pressed = False
        end = np.array([event.xdata, event.ydata], float)
        self.distance = np.sqrt(((self.init - end)**2).sum())
        plt.close()

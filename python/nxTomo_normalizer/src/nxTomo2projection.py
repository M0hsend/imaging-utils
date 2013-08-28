#! /usr/bin/env python
'''
 Copyright 2013 Diamond Light Source Ltd.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

@author: mark.basham@diamond.ac.uk
'''

import os
import optparse
import Image
import json

import numpy as np

from nxTomo_normalizer import extract_flat_corrected_projections

if __name__ == "__main__":
    usage = "%prog [options]"
    parser = optparse.OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-i", "--input", dest="input", help="input json file")
    parser.add_option("-o", "--output", dest="output", help="output json file")
    parser.add_option("-d", "--data", dest="data", help="input hdf5 file")
    parser.add_option("-r", "--result", dest="result", help="output hdf5 file")
    parser.add_option("-l", "--log", dest="log", help="log file")

    (options, args) = parser.parse_args()

    parameters = json.load(open(options.input))

    for i in range(options.begin, options.begin + options.slices, options.num_slices):
        print i
        end = min(i + options.num_slices, options.begin + options.slices)
        data = extract_flat_corrected_projections(args[0], i, end)
        for j in range(data.shape[0]):
            im = data[j, :, :]
            im = im.astype(np.float32)
            im = Image.fromarray(im)
            #im = im.convert('I;16')

            filename = os.path.join(args[1], options.format % (i + j))
            print("saving file to %s" % (filename))
            im.save(filename)

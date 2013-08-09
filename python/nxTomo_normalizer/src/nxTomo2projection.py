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

import numpy as np

from nxTomo_normalizer import extract_flat_corrected_projections

if __name__ == "__main__":
    usage = "%prog [options] input_nexus output_directory"
    parser = optparse.OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-b", "--begin", dest="begin", help="projection to begin from", default=0, type='int')
    parser.add_option("-s", "--slices", dest="slices", help="number of projections to process", default=-1, type='int')
    parser.add_option("-f", "--format", dest="format", help="format for the output files", default="p_%05d.tif")
    parser.add_option("-n", "--number_of_slices_per_read", dest="num_slices", help="The number of slices which will be read into memory at a time", default=16, type='int')

    (options, args) = parser.parse_args()

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

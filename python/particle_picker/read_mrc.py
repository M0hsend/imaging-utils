
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


import numpy as np
from os import stat
from os.path import splitext


def read_rec(filename, flip_z=True):
    rec_header_dtd = \
        [
            ("nx", "i4"),
            ("ny", "i4"),
            ("nz", "i4"),

            ("mode", "i4"),  # Types of pixels in the image:
                             #  0 = unsigned or signed bytes [imodFlags]
                             #  1 = signed short integers (16 bits)
                             #  2 = float (32 bits)
                             #  3 = short * 2, (used for complex data)
                             #  4 = float * 2, (used for complex data)
                             #  6 = unsigned 16-bit ints (non-standard)
                             # 16 = unsigned char * 3 (for rgb data)

            ("nxstart", "i4"),
            ("nystart", "i4"),
            ("nzstart", "i4"),

            ("mx", "i4"),
            ("my", "i4"),
            ("mz", "i4"),

            ("xlen", "f4"),
            ("ylen", "f4"),
            ("zlen", "f4"),

            ("alpha", "f4"),
            ("beta", "f4"),
            ("gamma", "f4"),

            ("mapc", "i4"),
            ("mapr", "i4"),
            ("maps", "i4"),

            ("amin", "f4"),
            ("amax", "f4"),
            ("amean", "f4"),

            ("ispg", "i4"),
            ("next", "i4"),
            ("creatid", "i2"),
            ("extra_data", "V30"),

            ("nint", "i2"),
            ("nreal", "i2"),

            ("extra_data2", "V20"),

            ("imodStamp", "i4"),
            ("imodFlags", "i4"),

            ("idtype", "i2"),
            ("lens", "i2"),
            ("nd1", "i2"),
            ("nd2", "i2"),
            ("vd1", "i2"),
            ("vd2", "i2"),

            ("triangles", "f4", 6),

            ("xorg", "f4"),
            ("yorg", "f4"),
            ("zorg", "f4"),

            ("cmap", "S4"),
            ("stamp", "u1", 4),

            ("rms", "f4"),

            ("nlabl", "i4"),
            ("labels", "S80", 10)
        ]

    rec_header_dtype = np.dtype(rec_header_dtd)
    assert rec_header_dtype.itemsize == 1024

    fd = open(filename, 'rb')
    stats = stat(filename)

    hdr_str = fd.read(rec_header_dtype.itemsize)
    header = np.ndarray(shape=(), dtype=rec_header_dtype, buffer=hdr_str)

    # Seek header
    if header['next'] > 0:
        fd.seek(header['next'])  # ignore extended header

    mode = header['mode']
    # BitOrder: little or big endian
    if header['stamp'][0] == 68 and header['stamp'][1] == 65:
        bo = "<"
    else:
        bo = ">"
    sign = "i1" if header['imodFlags'] == 1 else "u1"  # signed or unsigned

    #     0     1     2    3     4    5   6    7  8  9 10 11 12 13 14 15  16
    d = [sign, "i2", "f", "c4", "c8", 0, "u2", 0, 0, 0, 0, 0, 0, 0, 0, 0, "u1"]
    s = [1,     2,    4,   4,    8,   0,  2,   0, 0, 0, 0, 0, 0, 0, 0, 0,  3]
    dtype = d[mode]
    dsize = s[mode]

    # data dimensions
    nx, ny, nz = header['nx'], header['ny'], header['nz']
    img_size = nx * ny * nz * dsize
    if mode == 6:
        fd.read(1024)
    img_str = fd.read(img_size)
    dtype = bo + dtype

    # Make sure that we have readed the whole file
    assert not fd.read()
    assert stats.st_size == header.itemsize + img_size + 1024 * (mode == 6)

    fd.close()

    if mode == 16:
        data = np.ndarray(shape=(nx, ny, nz, 3), dtype=dtype, buffer=img_str)
        if flip_z:
            data = data.transpose((1, 0, 2, 3)).copy()
    else:
        data = np.ndarray(shape=(nx, ny, nz), dtype=dtype, buffer=img_str)
        if flip_z:
            data = data.transpose((1, 0, 2)).copy()

    return header, data

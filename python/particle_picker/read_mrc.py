
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


def read_rec(filename, flip_z=False):
    rec_header_dtd = \
    [
        ("nx", "i4"),              # Number of columns
        ("ny", "i4"),              # Number of rows
        ("nz", "i4"),              # Number of sections

        ("mode", "i4"),            # Types of pixels in the image. Values used by IMOD:
                                   #  0 = unsigned or signed bytes depending on flag in imodFlags
                                   #  1 = signed short integers (16 bits)
                                   #  2 = float (32 bits)
                                   #  3 = short * 2, (used for complex data)
                                   #  4 = float * 2, (used for complex data)
                                   #  6 = unsigned 16-bit integers (non-standard)
                                   # 16 = unsigned char * 3 (for rgb data, non-standard)

        ("nxstart", "i4"),         # Starting point of sub-image (not used in IMOD)
        ("nystart", "i4"),
        ("nzstart", "i4"),

        ("mx", "i4"),              # Grid size in X, Y and Z
        ("my", "i4"),
        ("mz", "i4"),

        ("xlen", "f4"),            # Cell size; pixel spacing = xlen/mx, ylen/my, zlen/mz
        ("ylen", "f4"),
        ("zlen", "f4"),

        ("alpha", "f4"),           # Cell angles - ignored by IMOD
        ("beta", "f4"),
        ("gamma", "f4"),

        # These need to be set to 1, 2, and 3 for pixel spacing to be interpreted correctly
        ("mapc", "i4"),            # map column  1=x,2=y,3=z.
        ("mapr", "i4"),            # map row     1=x,2=y,3=z.
        ("maps", "i4"),            # map section 1=x,2=y,3=z.

        # These need to be set for proper scaling of data
        ("amin", "f4"),            # Minimum pixel value
        ("amax", "f4"),            # Maximum pixel value
        ("amean", "f4"),           # Mean pixel value

        ("ispg", "i4"),            # space group number (ignored by IMOD)
        ("next", "i4"),            # number of bytes in extended header (called nsymbt in MRC standard)
        ("creatid", "i2"),         # used to be an ID number, is 0 as of IMOD 4.2.23
        ("extra_data", "V30"),     # (not used, first two bytes should be 0)

        # These two values specify the structure of data in the extended header; their meaning depend on whether the
        # extended header has the Agard format, a series of 4-byte integers then real numbers, or has data
        # produced by SerialEM, a series of short integers. SerialEM stores a float as two shorts, s1 and s2, by:
        # value = (sign of s1)*(|s1|*256 + (|s2| modulo 256)) * 2**((sign of s2) * (|s2|/256))
        ("nint", "i2"),            # Number of integers per section (Agard format) or number of bytes per section (SerialEM format)
        ("nreal", "i2"),           # Number of reals per section (Agard format) or bit
                                   # Number of reals per section (Agard format) or bit
                                   # flags for which types of short data (SerialEM format):
                                   # 1 = tilt angle * 100  (2 bytes)
                                   # 2 = piece coordinates for montage  (6 bytes)
                                   # 4 = Stage position * 25    (4 bytes)
                                   # 8 = Magnification / 100 (2 bytes)
                                   # 16 = Intensity * 25000  (2 bytes)
                                   # 32 = Exposure dose in e-/A2, a float in 4 bytes
                                   # 128, 512: Reserved for 4-byte items
                                   # 64, 256, 1024: Reserved for 2-byte items
                                   # If the number of bytes implied by these flags does
                                   # not add up to the value in nint, then nint and nreal
                                   # are interpreted as ints and reals per section

        ("extra_data2", "V20"),    # extra data (not used)

        ("imodStamp", "i4"),       # 1146047817 indicates that file was created by IMOD
        ("imodFlags", "i4"),       # Bit flags: 1 = bytes are stored as signed

        # Explanation of type of data
        ("idtype", "i2"),          # ( 0 = mono, 1 = tilt, 2 = tilts, 3 = lina, 4 = lins)
        ("lens", "i2"),
        ("nd1", "i2"),             # for idtype = 1, nd1 = axis (1, 2, or 3)
        ("nd2", "i2"),
        ("vd1", "i2"),             # vd1 = 100. * tilt increment
        ("vd2", "i2"),             # vd2 = 100. * starting angle

        # Current angles are used to rotate a model to match a new rotated image.  The three values in each set are
        # rotations about X, Y, and Z axes, applied in the order Z, Y, X.
        ("triangles", "f4", 6),    # 0,1,2 = original:  3,4,5 = current

        ("xorg", "f4"),            # Origin of image
        ("yorg", "f4"),
        ("zorg", "f4"),

        ("cmap", "S4"),            # Contains "MAP "
        ("stamp", "u1", 4),        # First two bytes have 17 and 17 for big-endian or 68 and 65 for little-endian

        ("rms", "f4"),             # RMS deviation of densities from mean density

        ("nlabl", "i4"),           # Number of labels with useful data
        ("labels", "S80", 10)      # 10 labels of 80 charactors
    ]

    rec_header_dtype = np.dtype(rec_header_dtd)
    assert rec_header_dtype.itemsize == 1024

    fd = open(filename, 'rb')
    stats = stat(filename)

    hdr_str = fd.read(rec_header_dtype.itemsize)
    header = np.ndarray(shape=(), dtype=rec_header_dtype, buffer=hdr_str)

    # Seek extended header
    if header['next'] > 0:
        fd.seek(rec_header_dtype.itemsize + header['next'])  # ignore extended header

    mode = header['mode']
    bo = "<" if header['stamp'][0] == 68 and header['stamp'][1] == 65 else "<" # BitOrder: little or big endian
    sign = "i1" if header['imodFlags'] == 1 else "u1" # signed or unsigned
            # 0     1     2     3     4     5     6     7     8     9     10    11    12    13    14    15    16
    dtype = [sign, "i2", "f",  "c4", "c8", None, "u2", None, None, None, None, None, None, None, None, None, "u1"][mode]
    dsize = [ 1,    2,    4,    4,    8,    0,    2,    0,    0,    0,    0,    0,    0,    0,    0,    0,    3][mode]

    # data dimensions
    nx, ny, nz = header['nx'], header['ny'], header['nz']
    img_size = nx * ny * nz * dsize
    img_str = fd.read(img_size)
    dtype = bo + dtype

    # Make sure that we have readed the whole file
    assert not fd.read()
    assert stats.st_size == header.itemsize + img_size

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

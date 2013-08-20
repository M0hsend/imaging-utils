import pytest
import nxTomo_normalizer as nxt
import os

FILE_LOCATION = './test_data/repacked.nxs'


def test_metamanager_key_reading():
    mm = nxt.MetaManager(FILE_LOCATION)
    assert (len(mm.get_keys()) == 2191)
    assert (len(mm.get_projection_positions()) == 1801)
    assert (len(mm.get_dark_positions()) == 20)
    assert (len(mm.get_flat_positions()) == 370)


def test_datamanager():
    dm = nxt.DataManager(FILE_LOCATION)
    assert(dm.get_frames([4, 5, 6, 7, 8]).shape == (5, 21, 32))
    assert(dm.get_sino_frames([4, 5, 6, 7], 10, 12).shape == (4, 2, 32))

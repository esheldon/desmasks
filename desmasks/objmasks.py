from __future__ import print_function
import numpy as np
import esutil as eu
from . import files


def load_tile_objmask(tilename):

    fname = files.get_objmask_file(tilename)

    print('loading objmask from:', fname)
    return ObjMask(fname)


class ObjMask(object):
    """
    object masking
    """
    def __init__(self, fname):
        self._fname = fname
        self._load_mask()

    def _load_mask(self):

        data = np.fromfile(self._fname, dtype='i8', sep=' ')
        nrows = data.size//2

        data = data.reshape((nrows, 2))
        self.objids = data[:, 1]

    def is_masked(self, objids):
        """
        check if the input objids is in the mask
        """

        is_masked = np.zeros(objids.size, dtype='bool')
        minput, mdata = eu.numpy_util.match(objids, self.objids)
        is_masked[minput] = True

        return is_masked

    def is_unmasked(self, objids):
        """
        check if the input objids is in the mask
        """
        return ~self.is_masked(objids)

    def get_mask_flags(self, objids):
        """
        get mask values (not from bounds)
        """

        mask_flags = np.zeros(objids.size, dtype='i4')
        is_masked = self.is_masked(objids)

        mask_flags[is_masked] = 64

        return mask_flags

import h5py as h5
import numpy as np


class VDSFileOps(object):
    """
    A class to perform file operations using Virtual dataset.
    Not the best code ever written, but abstracts away the nastiness. 
    """
    def __init__(self, source_path_pattern, key, target_path, file_numbers):
        self.key = key
        self.source_path_pattern = source_path_pattern
        self.target_path = target_path
        self.file_numbers = file_numbers
        self.outfile = h5.File(self.target_path)
        self.outfile.require_group(key)

    def make_linked_stack(self, fullname):
        """
        Actually makes the stacked dataset. This is a separate method since h5py's visit 
        items does not follow external links.
        
        fullname
            string key to the dataset to be converted into a stacked VDS
        """
        datashape = h5.File(self.source_path_pattern % (self.file_numbers[0]))[fullname].shape
        outshape = (len(self.file_numbers), ) + datashape
        TGT = h5.VirtualTarget(self.target_path, fullname, shape=outshape)
        k = 0
        VMlist = []
        for fnum in self.file_numbers:
            print fnum
            source_path = self.source_path_pattern % (fnum)
            VSRC = h5.VirtualSource(source_path, fullname, shape=datashape)
            VM = h5.VirtualMap(VSRC, TGT[k:(k + 1):1], dtype=np.float)
            VMlist.append(VM)
            k += 1
        d = self.outfile.create_virtual_dataset(VMlist=VMlist, fillvalue=0)
        for key, val in h5.File(self.source_path_pattern % (self.file_numbers[0]))[fullname].attrs.iteritems():
            self.outfile[fullname].attrs[key] = val

    def _visit_fields(self,name, obj):
        """
        The iterator method for concatenate sets. To be used with visititems.
        """
        fullname = self.key + '/' + name
        if (h5._hl.group.Group == type(obj)):
            print "requiring"
            self.outfile.require_group(fullname)
            for key,val in obj.attrs.iteritems():
                self.outfile[fullname].attrs[key] = val
        else:
            self.make_linked_stack(fullname)

    def concatenate_files(self):
        """
        This uses the h5py visititems to clone all the attributes in an entry
        within the file ranges. It unfortunately does not follow links:
        a separate call to make_linked_stack is suggested.
        """
        entry = h5.File(self.source_path_pattern % self.file_numbers[0])[key]
        entry.visititems(self._visit_fields)
        entry.file.close()
    
    def closeit(self):
        self.outfile.close()


file_nums = range(91371,91399)
infile_path = '/dls/staging/dls/i13-1/data/2016/mt14190-1/raw/%s.nxs'
outfile = '/dls/i13-1/data/2016/mt14190-1/processing/tomo_processed/ptycho/ptycho_vds_testeroo.h5'
key = 'entry1/instrument'
a = VDSFileOps(infile_path, key, outfile, file_nums)
a.concatenate_files()
a.make_linked_stack('/entry1/instrument/merlin_sw_hdf/data')
a.closeit()

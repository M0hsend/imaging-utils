'''
Created on 28 Nov 2018

@author: ssg37927
'''
import unittest
from IdentifyPotentialConversions import check_differences
from mib2hdf import convert

class Test(unittest.TestCase):


    def testName(self):
        [to_convert_list, mib_files_list] = check_differences('e02', '2018', 'em20527-1')
        if bool(to_convert_list):
            convert('e02', '2018', 'em20527-1', mib_files_list)
        else:
            print('Nothing to convert here!')
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
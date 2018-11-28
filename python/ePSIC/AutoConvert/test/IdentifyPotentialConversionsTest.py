'''
Created on 28 Nov 2018

@author: ssg37927
'''
import unittest
from IdentifyPotentialConversions import check_differences

class Test(unittest.TestCase):


    def testName(self):
        check_differences('e02', '2018', 'em20498-1')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
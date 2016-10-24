import unittest
from tests.test_jinjasql import JinjaSqlTest

def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(JinjaSqlTest))
    return suite

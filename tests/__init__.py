import sys
import unittest
from tests.test_jinjasql import JinjaSqlTest

def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(JinjaSqlTest))

    if sys.version_info <= (3, 4):
        from tests.test_django import DjangoTest
        suite.addTest(unittest.makeSuite(DjangoTest))

    return suite

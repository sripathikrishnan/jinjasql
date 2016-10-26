import unittest
from tests.test_jinjasql import JinjaSqlTest
from tests.test_django import DjangoTest
def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(JinjaSqlTest))
    suite.addTest(unittest.makeSuite(DjangoTest))
    return suite

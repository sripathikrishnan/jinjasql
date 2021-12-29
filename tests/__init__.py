import sys
import unittest
from tests.test_jinjasql import JinjaSqlTest
from tests.test_real_database import PostgresTest, MySqlTest

def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(JinjaSqlTest))
    suite.addTest(unittest.makeSuite(PostgresTest))
    suite.addTest(unittest.makeSuite(MySqlTest))

    if sys.version_info <= (3, 4):
        from tests.test_django import DjangoTest
        suite.addTest(unittest.makeSuite(DjangoTest))

    return suite

from testcontainers.postgres import PostgresContainer
import sqlalchemy
import unittest
from jinjasql import JinjaSql

class PostgresTest(unittest.TestCase):

    # Core idea inspired from 
    # https://stackoverflow.com/questions/8416208/in-python-is-there-a-good-idiom-for-using-context-managers-in-setup-teardown
    # 
    # Override the run method to automatically
    # a. launch a postgres docker container
    # b. create a sqlalchemy connection 
    # c. At the end of all the tests, kill the docker container
    def run(self, result=None):
        with PostgresContainer("postgres:9.5") as postgres:
            self.db_url = postgres.get_connection_url()
            self.engine = sqlalchemy.create_engine(self.db_url)
            super(PostgresTest, self).run(result)

    def test_bind_array(self):
        'It should be possible to bind arrays in a query'
        j = JinjaSql()
        data = {
            "some_num": 1,
            "some_array": [1,2,3]
        }
        template = """
            SELECT {{some_num}} = ANY({{some_array}})
        """
        query, params = j.prepare_query(template, data)
        result = self.engine.execute(query, params).fetchone()
        self.assertTrue(result[0])

if __name__ == '__main__':
    unittest.main()
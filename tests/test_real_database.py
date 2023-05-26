from testcontainers.postgres import PostgresContainer
from testcontainers.mysql import MySqlContainer
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
    # c. at the end of the test, kill the docker container
    def run(self, result=None):
        with PostgresContainer("postgres:9.5") as postgres:
            self.engine = sqlalchemy.create_engine(postgres.get_connection_url())
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
        with self.engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(query), params).fetchone()
        self.assertTrue(result[0])
    
    def test_quoted_tables(self):
        j = JinjaSql()
        data = {
            "all_tables": ("information_schema", "tables")
        }
        template = """
            select table_name from {{all_tables|identifier}}
            where table_name = 'pg_user'
        """
        query, params = j.prepare_query(template, data)
        with self.engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(query), params).fetchall()
        self.assertEqual(len(result), 1)

class MySqlTest(unittest.TestCase):
    def run(self, result=None):
        with MySqlContainer("mysql:5.7.17") as mysql:
            self.engine = sqlalchemy.create_engine(mysql.get_connection_url())
            super(MySqlTest, self).run(result)

    def test_quoted_tables(self):
        j = JinjaSql(identifier_quote_character='`')
        data = {
            "all_tables": ("information_schema", "tables")
        }
        template = """
            select table_name from {{all_tables|identifier}}
            where table_name = 'SESSION_STATUS'
        """
        query, params = j.prepare_query(template, data)
        with self.engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(query), params).fetchall()
        self.assertEqual(len(result), 1)

if __name__ == '__main__':
    unittest.main()
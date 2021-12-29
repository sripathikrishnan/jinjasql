from __future__ import unicode_literals
import unittest
from jinja2 import DictLoader
from jinja2 import Environment
from jinjasql import JinjaSql
from jinjasql.core import InvalidBindParameterException
from datetime import date
from yaml import safe_load_all
from os.path import dirname, abspath, join


YAML_TESTS_ROOT = join(dirname(abspath(__file__)), "yaml")

_DATA = {
    "etc": {
        "columns": "project, timesheet, hours",
        "lt": "<",
        "gt": ">",

    },
    "request": {
        "project": {
            "id": 123,
            "name": "Acme Project"
        },
        "project_id": 123,
        "days": ["mon", "tue", "wed", "thu", "fri"],
        "day": "mon",
        "start_date": date.today(),
    },
    "session": {
        "user_id": u"sripathi"
    }
}

class JinjaSqlTest(unittest.TestCase):
    def setUp(self):
        self.j = JinjaSql()

    def test_import(self):
        utils = """
        {% macro print_where(value) -%}
        WHERE dummy_col = {{value}}
        {%- endmacro %}
        """
        source = """
        {% import 'utils.sql' as utils %}
        select * from dual {{ utils.print_where(100) }}
        """
        loader = DictLoader({"utils.sql" : utils})
        env = Environment(loader=loader)

        j = JinjaSql(env)
        query, bind_params = j.prepare_query(source, _DATA)
        expected_query = "select * from dual WHERE dummy_col = %s"
        self.assertEqual(query.strip(), expected_query.strip())
        self.assertEqual(len(bind_params), 1)
        self.assertEqual(list(bind_params)[0], 100)

    def test_include(self):
        where_clause = """where project_id = {{request.project_id}}"""
        
        source = """
        select * from dummy {% include 'where_clause.sql' %}
        """
        loader = DictLoader({"where_clause.sql" : where_clause})
        env = Environment(loader=loader)

        j = JinjaSql(env)
        query, bind_params = j.prepare_query(source, _DATA)
        expected_query = "select * from dummy where project_id = %s"
        self.assertEqual(query.strip(), expected_query.strip())
        self.assertEqual(len(bind_params), 1)
        self.assertEqual(list(bind_params)[0], 123)

    def test_precompiled_template(self):
        source = "select * from dummy where project_id = {{ request.project_id }}"
        j = JinjaSql()
        query, bind_params = j.prepare_query(j.env.from_string(source), _DATA)
        expected_query = "select * from dummy where project_id = %s"
        self.assertEqual(query.strip(), expected_query.strip())

    def test_large_inclause(self):
        num_of_params = 50000
        alphabets = ['A'] * num_of_params
        source = "SELECT 'x' WHERE 'A' in {{alphabets | inclause}}"
        j = JinjaSql()
        query, bind_params = j.prepare_query(source, {"alphabets": alphabets})
        self.assertEqual(len(bind_params), num_of_params)
        self.assertEqual(query, "SELECT 'x' WHERE 'A' in (" + "%s," * (num_of_params - 1) + "%s)")

    def test_identifier_filter(self):
        j = JinjaSql()
        template = 'select * from {{table_name | identifier}}'
        
        tests = [
            ('users', 'select * from "users"'),
            (('myschema', 'users'), 'select * from "myschema"."users"'),
            ('a"b', 'select * from "a""b"'),
            (('users',), 'select * from "users"'),
        ]
        for test in tests:
            query, _ = j.prepare_query(template, {'table_name': test[0]})
            self.assertEqual(query, test[1])


    def test_identifier_filter_backtick(self):
        j = JinjaSql(identifier_quote_character='`')
        template = 'select * from {{table_name | identifier}}'
        
        tests = [
            ('users', 'select * from `users`'),
            (('myschema', 'users'), 'select * from `myschema`.`users`'),
            ('a`b', 'select * from `a``b`'),
        ]
        for test in tests:
            query, _ = j.prepare_query(template, {'table_name': test[0]})
            self.assertEqual(query, test[1])

def generate_yaml_tests():
    file_path = join(YAML_TESTS_ROOT, "macros.yaml")
    with open(file_path) as f:
        configs = safe_load_all(f)
        for config in configs:
            yield (config['name'], _generate_test(config))

def _generate_test(config):
    def yaml_test(self):
        source = config['template']
        for (param_style, expected_sql) in config['expected_sql'].items():
            jinja = JinjaSql(param_style=param_style)
            query, bind_params = jinja.prepare_query(source, _DATA)

            if 'expected_params' in config:
                if param_style in ('pyformat', 'named'):
                    expected_params = config['expected_params']['as_dict']
                else:
                    expected_params = config['expected_params']['as_list']
                self.assertEqual(list(bind_params), expected_params)

            self.assertEqual(query.strip(), expected_sql.strip())

    return yaml_test

for test in generate_yaml_tests():
    test_name = test[0]
    test_function = test[1]
    setattr(JinjaSqlTest, test_name, test_function)

if __name__ == '__main__':
    unittest.main()
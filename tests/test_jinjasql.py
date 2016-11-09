from __future__ import unicode_literals
import unittest
from jinja2 import DictLoader
from jinja2 import Environment
from jinjasql import JinjaSql
from jinjasql.core import MissingInClauseException, InvalidBindParameterException
from datetime import date
from yaml import load_all
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

    def test_missed_inclause_raises_exception(self):
        source = """select * from timesheet 
                    where day in {{request.days}}"""
        self.assertRaises(MissingInClauseException, self.j.prepare_query, source, _DATA)

    def test_inclause_with_dictionary(self):
        source = """select * from timesheet 
                    where project in {{request.project}}"""
        self.assertRaises(InvalidBindParameterException, self.j.prepare_query, source, _DATA)

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
        self.assertEquals(query.strip(), expected_query.strip())
        self.assertEquals(len(bind_params), 1)
        self.assertEquals(bind_params[0], 100)

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
        self.assertEquals(query.strip(), expected_query.strip())
        self.assertEquals(len(bind_params), 1)
        self.assertEquals(bind_params[0], 123)

def generate_yaml_tests():
    file_path = join(YAML_TESTS_ROOT, "macros.yaml")
    with open(file_path) as f:
        configs = load_all(f)
        for config in configs:
            yield (config['name'], _generate_test(config))

def _generate_test(config):
    def yaml_test(self):
        source = config['template']
        for param_style, expected_sql in config['expected_sql'].iteritems():
            jinja = JinjaSql(param_style=param_style)
            query, bind_params = jinja.prepare_query(source, _DATA)

            if 'expected_params' in config:
                if param_style in ('pyformat', 'named'):
                    expected_params = config['expected_params']['as_dict']
                else:
                    expected_params = config['expected_params']['as_list']
                self.assertEquals(bind_params, expected_params)

            self.assertEquals(query.strip(), expected_sql.strip())

    return yaml_test

for test in generate_yaml_tests():
    test_name = test[0]
    test_function = test[1]
    setattr(JinjaSqlTest, test_name, test_function)

if __name__ == '__main__':
    unittest.main()
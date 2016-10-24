import unittest
from jinja2sql import JinjaSql

source = """
{% macro print_where() -%}
    WHERE
{%- endmacro %}
SELECT project, timesheet, hours
FROM timesheet
{{ print_where() | sqlsafe }} project_id = {{request.project_id}} 
and user_id = {{session.user_id | upper}}
"""

data = {
    "request": {
        "project_id": 123
    },
    "session": {
        "user_id": "sripathi"
    }
}

class JinjaSqlTest(unittest.TestCase):
    def test_bind_params(self):
        j = JinjaSql()
        query, bind_params = j.prepare_query(source, data)
        print query
        print bind_params

if __name__ == '__main__':
    unittest.main()
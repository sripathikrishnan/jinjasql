import unittest
from jinjasql import JinjaSql

_DATA = {
    "etc": {
        "columns": "project, timesheet, hours",
        "lt": "<",
        "gt": ">",

    },
    "request": {
        "project_id": 123,
    },
    "session": {
        "user_id": u"sripathi"
    }
}

class JinjaSqlTest(unittest.TestCase):
    def test_bind_params(self):
        source = """
            SELECT project, timesheet, hours
            FROM timesheet
            WHERE project_id = {{request.project_id}} 
            and user_id = {{ session.user_id }}
        """
        j = JinjaSql()
        query, bind_params = j.prepare_query(source, _DATA)
        self.assertEquals(bind_params, [123, u'sripathi'])

    def test_sqlsafe(self):
        source = """SELECT {{etc.columns | sqlsafe}} FROM timesheet"""
        j = JinjaSql()
        query, bind_params = j.prepare_query(source, _DATA)
        self.assertEquals(query, "SELECT project, timesheet, hours FROM timesheet")

    def test_macro(self):
        source = """
        {% macro OPTIONAL_AND(condition, expression, value) -%}
            {%- if condition -%}AND {{expression | sqlsafe}} {{value}} {%- endif-%}
        {%- endmacro -%}
        SELECT 'x' from dual
        WHERE 1=1 
        {{ OPTIONAL_AND(request.project_id != -1, 
            "project_id = ", request.project_id) | sqlsafe }}
        {{ OPTIONAL_AND(request.unknown_column, 
            "some_column = ", request.unknown_column) | sqlsafe -}}
        AND fixed_column = {{session.user_id}}
        """

        expected_query = """
        SELECT 'x' from dual
        WHERE 1=1 
        AND project_id =  %s
        AND fixed_column = %s"""

        j = JinjaSql()
        query, bind_params = j.prepare_query(source, _DATA)

        self.assertEquals(query.strip(), query.strip())
        self.assertEquals(bind_params, [123, u'sripathi'])

    def test_html_escape(self):
        """Check that jinja doesn't escape HTML characters"""

        source = """select 'x' from dual where X {{etc.lt | sqlsafe}} 1"""
        j = JinjaSql()
        query, bind_params = j.prepare_query(source, _DATA)
        self.assertEquals(query, "select 'x' from dual where X < 1")

if __name__ == '__main__':
    unittest.main()
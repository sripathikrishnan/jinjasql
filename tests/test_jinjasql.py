from __future__ import unicode_literals
import unittest
from jinjasql import JinjaSql
from jinjasql.core import MissingInClauseException, InvalidBindParameterException
from datetime import date

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

    def test_bind_params(self):
        source = """
            SELECT project, timesheet, hours
            FROM timesheet
            WHERE project_id = {{request.project_id}} 
            and user_id = {{ session.user_id }}
        """
        query, bind_params = self.j.prepare_query(source, _DATA)
        self.assertEquals(bind_params, [123, u'sripathi'])

    def test_sqlsafe(self):
        source = """SELECT {{etc.columns | sqlsafe}} FROM timesheet"""
        query, bind_params = self.j.prepare_query(source, _DATA)
        self.assertEquals(query, "SELECT project, timesheet, hours FROM timesheet")

    def test_macro(self):
        source = """
        {% macro OPTIONAL_AND(condition, expression, value) -%}
            {%- if condition -%}AND {{expression | sqlsafe}} {{value}} {%- endif-%}
        {%- endmacro -%}
        SELECT 'x' from dual
        WHERE 1=1 
        {{ OPTIONAL_AND(request.project_id != -1, 
            "project_id = ", request.project_id)}}
        {{ OPTIONAL_AND(request.unknown_column, 
            "some_column = ", request.unknown_column) -}}
        AND fixed_column = {{session.user_id}}
        """

        expected_query = """
        SELECT 'x' from dual
        WHERE 1=1 
        AND project_id =  %s
        AND fixed_column = %s"""

        query, bind_params = self.j.prepare_query(source, _DATA)

        self.assertEquals(query.strip(), query.strip())
        self.assertEquals(bind_params, [123, u'sripathi'])

    def test_html_escape(self):
        """Check that jinja doesn't escape HTML characters"""

        source = """select 'x' from dual where X {{etc.lt | sqlsafe}} 1"""
        query, bind_params = self.j.prepare_query(source, _DATA)
        self.assertEquals(query, "select 'x' from dual where X < 1")

    def test_explicit_in_clause(self):
        source = """select * from timesheet 
                    where day in {{request.days | inclause}}"""
        query, bind_params = self.j.prepare_query(source, _DATA)
        self.assertEquals(query, """select * from timesheet 
                    where day in (%s,%s,%s,%s,%s)""")
        self.assertEquals(bind_params, ["mon", "tue", "wed", "thu", "fri"])

    def test_missed_inclause_raises_exception(self):
        source = """select * from timesheet 
                    where day in {{request.days}}"""
        self.assertRaises(MissingInClauseException, self.j.prepare_query, source, _DATA)

    def test_inclause_with_dictionary(self):
        source = """select * from timesheet 
                    where project in {{request.project}}"""
        self.assertRaises(InvalidBindParameterException, self.j.prepare_query, source, _DATA)

    def test_macro_output_is_marked_safe(self):
        source = """
        {% macro week(value) -%}
        some_sql_function({{value}})
        {%- endmacro %}
        SELECT 'x' from dual WHERE created_date > {{ week(request.start_date) }}
        """
        query, bind_params = self.j.prepare_query(source, _DATA)
        expected_query = "SELECT 'x' from dual WHERE created_date > some_sql_function(%s)"
        self.assertEquals(query.strip(), expected_query.strip())
        self.assertEquals(len(bind_params), 1)
        self.assertEquals(bind_params[0], date.today())
    
    def test_set_block(self):
        source = """
        {% set columns -%}
        project, timesheet, hours
        {%- endset %}
        select {{ columns | sqlsafe }} from dual
        """
        query, bind_params = self.j.prepare_query(source, _DATA)
        expected_query = "select project, timesheet, hours from dual"
        self.assertEquals(query.strip(), expected_query.strip())

if __name__ == '__main__':
    unittest.main()
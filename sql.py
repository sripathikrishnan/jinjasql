from jinja2 import Environment
from jinja2 import Template
from jinja2.ext import Extension
from jinja2.lexer import Token

from threading import local
_thread_local = local()
    

source = """
{% macro print_where() -%}
    WHERE
{%- endmacro %}
SELECT project, timesheet, hours
FROM timesheet
{{ print_where() | safe }} project_id = {{request.project_id}} 
and user_id = {{session.user_id}}
"""

data = {
    "request": {
        "project_id": 123
    },
    "session": {
        "user_id": 923
    }
}

class SqlExtension(Extension):
    def filter_stream(self, stream):
        """
        Token(10, 'pipe', u'|')
        Token(10, 'name', 'capitalize')
        """
        while not stream.eos:
            token = next(stream)
            if token.test("variable_begin"):
                var_expr = []
                while not token.test("variable_end"):
                    var_expr.append(token)
                    token = next(stream)
                variable_end = token

                var_expr.append(Token(10, 'pipe', u'|'))
                var_expr.append(Token(10, 'name', u'bind_expression'))

                var_expr.append(variable_end)

                for token in var_expr:
                    print token.__repr__()
                    yield token
            else:
                yield token

class SqlSafe:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

def sql_safe(value):
    return SqlSafe(value)

def bind_expression(value):
    if isinstance(value, SqlSafe):
        return value
    from threading import local
    _thread_local.bind_params.append(value)
    return "%s"


env = Environment(extensions=[SqlExtension])
env.filters["bind_expression"] = bind_expression
env.filters["safe"] = sql_safe


def prepare_query(source, data):
    _thread_local.bind_params = []

    template = env.from_string(source)
    query = template.render(**data)

    bind_params = _thread_local.bind_params
    del _thread_local.bind_params
    return query, bind_params

query, bind_params = prepare_query(source, data)
print query
print bind_params

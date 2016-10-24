from jinja2 import Environment
from jinja2 import Template
from jinja2.ext import Extension
from jinja2.lexer import Token

from threading import local
_thread_local = local()

class SqlExtension(Extension):
    def filter_stream(self, stream):
        """
        We convert 
        {{ some.variable | filter1 | filter 2}}
            to 
        {{ some.variable | filter1 | filter 2 | bind}}
        
        ... for all variable declarations in the template

        This function is called by jinja2 immediately 
        after the lexing stage, but before the parser is called. 
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
                var_expr.append(Token(10, 'name', u'bind'))

                var_expr.append(variable_end)

                for token in var_expr:
                    yield token
            else:
                yield token

class SqlSafe:
    """Marker class to indicate the string 
    is safe to be inserted in a SQL Query"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

def sql_safe(value):
    """Filter to mark the value of an expression as safe for inserting
    in a SQL statement"""
    return SqlSafe(value)

def bind(value):
    """A filter that prints %s, and stores the value 
    in an array, so that it can be bound using a prepared statement

    This filter is automatically applied to every {{variable}} 
    during the lexing stage, so developers can't forget to bind
    """
    if isinstance(value, SqlSafe):
        return value
    _thread_local.bind_params.append(value)
    return "%s"

class JinjaSql(object):
    def __init__(self, env=None):
        if env:
            self.env = env
        else:
            self.env = Environment()
        self._prepare_environment()

    def _prepare_environment(self):
        self.env.add_extension(SqlExtension)
        self.env.filters["bind"] = bind
        self.env.filters["sqlsafe"] = sql_safe

    def prepare_query(self, source, data):
        template = self.env.from_string(source)
        return self._prepare_query(template, data)

    def _prepare_query(self, template, data):
        try:
            _thread_local.bind_params = []
            query = template.render(**data)
            bind_params = _thread_local.bind_params
            return query, bind_params
        finally:
            del _thread_local.bind_params

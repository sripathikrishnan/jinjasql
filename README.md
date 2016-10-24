# Generate SQL Queries using a Jinja2 Template. #

JinjaSql automatically tracks bind parameters, and returns an array
of all parameters that can be used to execute the query.

## Usage ##

```python

# Import the package
from jinjasql import JinjaSql

# This is the main class that wraps a Jinja Environment
j = JinjaSql()

# This is the template query
# You can use the full power of Jinja here - macros, conditions, loops what-have-you
template = """
    SELECT project, timesheet, hours
    FROM timesheet
    WHERE user_id = {{ user_id }}
    {% if project_id %}
    AND project_id = {{ project_id }}
    {% endif %}
"""

# This is the context that is passed to Jinja template
# It can contain lists, nested objects, even functions
data = {
    "project_id": 123,
    "user_id": u"sripathi"
}

# This is the core of this library
# `query` is the generated SQL query. Variables are replaced by %s
# `bind_params` is an array of parameters corresponding to the %s

query, bind_params = j.prepare_query(template, data)

# This is the query that is generated
expected_query = """
    SELECT project, timesheet, hours
    FROM timesheet
    WHERE user_id = %s
    
    AND project_id = %s
"""

# These are the bind parameters
self.assertEquals(bind_params, [u'sripathi', 123])
self.assertEquals(query.strip(), expected_query.strip())

# You can now use the query and bind parameters to execute the query
# For example, in django, you would do something like this - 

from django.db import connection
with connection.cursor() as cursor:
    cursor.execute(query, bind_params)
    for row in cursor.fetchall():
        # do something with the results
        pass
```

## Installing jinjasql ##

Pre-Requisites : 

1. python 2.x and pip.
2. jinja2 >= version 2.5

To install from PyPI (recommended) :

    pip install jinjasql
    
To install from source : 

    git clone https://github.com/hashedin/jinjasql
    cd jinjasql
    sudo python setup.py install

## License

jinjasql is licensed under the MIT License. See [LICENSE](https://github.com/hashedin/jinjasql/blob/master/LICENSE)

## Copyright 

(c) 2016 HashedIn Technologies Pvt. Ltd.

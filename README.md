# Generate SQL Queries using a Jinja Template, without worrying about SQL Injection #

[![Build Status](https://travis-ci.org/hashedin/jinjasql.svg?branch=master)](https://travis-ci.org/hashedin/jinjasql)

JinjaSQL is a template language for SQL statements and scripts. 
Since it's based in [Jinja2](http://jinja.pocoo.org/), 
you have all the power it offers - conditional statements, macros,
looping constructs, blocks, inheritance, and many more.

JinjaSQL automatically binds parameters that are inserted into the template.
After JinjaSQL evaluates the template, you get:

1. A Query with %s placeholders for the parameters
2. A List of values corresponding to the placeholdersthat need to be bound to the query

JinjaSQL doesn't actually execute the query - it only prepares the 
query and the bind parameters. You can execute the query using any 
database engine / driver you are working with.

For example, if you have a template like this -

```sql    
select username, sum(spend)
from transactions
where start_date > {{request.start_date}}
and end_date < {{request.end_date}}
{% if request.organization %}
and organization = {{request.organization}}
{% endif %}
```

then, depending on the parameters you provide, you get a query

```sql
select username, sum(spend)
from transaction
where start_date > %s
and end_date < %s
and organization = %s
```
with bind parameters = ['2016-10-10', '2016-10-20', 1321]

If `request.organization` was empty/falsy, the corresponding and clause
would be absent from the query, and the list of bind parameters
would not have the organization id.

## Why should I use JinjaSQL? ##

SQL code has a lot of repetition. With JinjaSQL, you can eliminate repetition and keep your SQL [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself). 

JinjaSQL lets you externalize your queries. You can keep your templates in files, in databases or in S3 or any place that makes sense for your application. 

## When to use JinjaSQL ##

JinjaSQL is *not* meant to replace your ORM. ORMs like those provided
by SQLAlchemy or Django are great for a variety of use cases, and should
be the default in most cases. But there are a few use cases where 
you really need the power of SQL.

Use JinjaSQL for - 

1. Reporting, business intelligence or dashboard like use cases
1. When you need aggregation/group by
1. Use cases that require data from multiple tables
1. Migration scripts & bulk updates that would benefit from macros

In all other use cases, you should reach to your ORM 
instead of writing SQL/JinjaSQL.

While JinjaSQL can handle insert/update statements, you are better off
using your ORM to handle such statements. JinjaSQL is mostly meant 
for dynamic select statements that an ORM cannot handle as well.

## Basic Usage ##

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

## How does JinjaSQL work? ##

### The bind filter ###

At it's core, JinjaSQL provides a filter called `bind`. This filter gobbles up whatever value is provided, and always emits the placeholder string %s. The actual value is then stored in a thread local list of bind parameters.

```python
jinja.prepare_query("select * from user where id = {{userid | bind}}", 
                    {userid: 143})
```

When this code is evaluated, the output query is `select * from user where id = %s`. 

### Pre-processing the Query Template ###

Manually applying the `bind` filter to every parameter is error-prone. Sooner than later, a developer will miss the filter, and it will lead to SQL Injection.

JinjaSQL automatically applies the bind filter to ALL variables. The query template is transformed before it is evaluated.

```sql
select * from user where id = {{userid}}
```

becomes 
```sql
select * from user where id = {{userid | bind}}
```

Jinja lets extensions to [rewrite the token stream](http://jinja.pocoo.org/docs/dev/extensions/#jinja2.ext.Extension.filter_stream). JinjaSQL looks for `variable_begin` and `variable_end` tokens in the stream, and rewrites the stream to include the `bind` filter as the last filter.

### Autoescape and JinjaSQL ###

Jinja has an autoescape feature. If turned on, it automatically HTML escapes variables. It does this by wrapping strings using the `Markup` class.

JinjaSQL builds on this functionality. JinjaSQL requires autoescape to be turned on. As a result, strings that are injected are wrapped using the Markup class. JinjaSQL uses this wrapper class as well to prevent double-binding of parameters.


## License

jinjasql is licensed under the MIT License. See [LICENSE](https://github.com/hashedin/jinjasql/blob/master/LICENSE)

## Copyright 

(c) 2016 HashedIn Technologies Pvt. Ltd.

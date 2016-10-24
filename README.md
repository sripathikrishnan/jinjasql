# Generate SQL Queries using a Jinja2 Template. #

JinjaSql automatically tracks bind parameters, and returns an array
of all parameters that can be used to execute the query.

## Installing jinjasql ##

Pre-Requisites : 

1. python 2.x and pip.
2. jinja2

To install from PyPI (recommended) :

    pip install jinjasql
    
To install from source : 

    git clone https://github.com/hashedin/jinjasql
    cd jinjasql
    sudo python setup.py install

## Usage ##

    from jinja2sql import JinjaSql

    template = """
        SELECT project, timesheet, hours
        FROM timesheet
        WHERE user_id = {{ user_id }}
        {% if project_id %}
        AND project_id = {{ project_id }}
        {% endif %}
    """

    data = {
        "project_id": 123,
        "user_id": u"sripathi"
    }

    j = JinjaSql()
    query, bind_params = j.prepare_query(template, data)

    expected_query = """
        SELECT project, timesheet, hours
        FROM timesheet
        WHERE user_id = %s
        AND project_id = %s
    """

    self.assertEquals(bind_params, [u'sripathi', 123])
    self.assertEquals(query.strip(), expected_query.strip())

    # You can now use the query and bind parameters to execute the query
    # For example, in django

    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(query, bind_params)
        for row in cursor.fetchall():
            # do something with the results
            pass


## License

jinjasql is licensed under the MIT License. See [LICENSE](https://github.com/hashedin/jinjasql/blob/master/LICENSE)

## Maintained By 

Sripathi Krishnan : @srithedabbler

Mailing List Stats [![Build Status](https://travis-ci.org/MetricsGrimoire/MailingListStats.svg?branch=master)](https://travis-ci.org/MetricsGrimoire/MailingListStats)
==================

Description
-----------
Mailing List Stats (`mlstats`) is a tool to parse and analyze mail boxes.
It is useful to retrieve and analyze mailing list archives.  The parsed
mail boxes are stored in a database.

`mlstats` is able to retrieve mailing lists from the web,
and store the data of every email in a database, from where to obtain
different kind of reports.

License
-------

Licensed under GNU General Public License (GPL), version 2 or later.


Download
--------

Releases:

* [https://github.com/MetricsGrimoire/MailingListStats/releases](https://github.com/MetricsGrimoire/MailingListStats/releases)

Latest version:

    $ git clone git://github.com/MetricsGrimoire/MailingListStats.git


Requirements
-------------
`mlstats` needs the following dependencies (either MySQL or PostgreSQL):

  * Python package "[SQLAlchemy](https://pypi.python.org/pypi/SQLAlchemy)"
  * MySQL:
    * Python package "[MySQL-python](https://pypi.python.org/pypi/MySQL-python/)"
    * MySQL-Server
  * PostgreSQL:
    * Python package "[psycopg2](https://pypi.python.org/pypi/psycopg2)"
    * PostgreSQL-Server (tested with 8.4 and 9.1)


Installation
------------
You can install MLStats running setup.py script:

    $ python setup.py install

If you don't have root privileges, use the `--prefix` option to indicate
the directory where `mlstats` will be installed. For more details, take a
look at the help of the installer:

    $ python setup.py install --help

You are ready to use `mlstats`.

## Running mlstats

### With MySQL

* If you just installed mysql, you may need to start the service before continuing. 
	* To do so on OS X, run `/usr/local/bin/mysql.server start`
* `max_allowed_packet`: Raise your `max_allowed_packet`-setting of your database. 1 or 16 MB might be too low (depends on your mailinglist). In the most cases 50 MB is a good value.
	* To set this at runtime, use `SET GLOBAL max_allowed_packet=16*1024*1024;` on the mysql prompt
* To have the privileges to create the database below, you'll want to run `mysql -u root` followed by a `CREATE USER` statement like: 

	```
	$ mysql -u root
	mysql> CREATE USER 'jeffrey'@'localhost' IDENTIFIED BY 'mypass';
	mysql> GRANT ALL PRIVILEGES ON * . * TO 'jeffrey'@'localhost';
	mysql> FLUSH PRIVILEGES;
	```

The MySQL backend requires the database already exists. Use the following
command to create the database. The tables will be automatically created 
when mlstats runs.

    mysql> create database mlstats;

You can now leave the mysql prompt by running `exit;`.

Assuming you have a MySQL database running on localhost, you might run mlstats
with these commonly used options (replace the text in ALL CAPS with your db username, 
db password and mailing list URL):

    $ mlstats --db-user=USERNAME --db-password=PASS http://URLOFYOURLIST

If you have a different configuration or need more options, more detailed information
about the options, can be learnt by running `mlstats --help`

### With Postgres

The postgres backend requires the database already exists. The creation
of tables must be done manually. There is a SQL script with the schema
in `db/data_model_pg.sql` that can be used for this purpose.

Analysis
--------

Analysis of mlstats data is completed by writing database queries. mlstats does the hard
work of parsing the mailing list archives and storing all of this data into a database 
that can be used to extract meaningful data about a mailing list. Because what is meaningful
varies by project, the flexibility of being able to write any query is a necessity.

While this does require a bit of knowledge about database queries, there are a few resources
to help you get started.

* Use the **[Database Schema](https://github.com/MetricsGrimoire/MailingListStats/wiki/Database-Schema)**
wiki page to learn more about the database structure. This will help you write your queries, but 
it also gives you a comprehensive list of everything that can be found in the database and 
retrieved in your queries.
* Because we don't want you to start from zero, use the **[Queries](https://github.com/MetricsGrimoire/MailingListStats/wiki/Queries)**
wiki page to find some commonly used queries and examples. If you have some interesting examples,
please add them to the wiki page.


Improving MailingListStats
---------------------------

Source code, wiki and submission of bug reports are accessible in [GitHub].

[GitHub]: https://github.com/MetricsGrimoire/MailingListStats

If you want to receive updates about new versions, and keep in touch
with the development team, consider subscribing to the [MetricsGrimoire mailing list][1].
It is a very low traffic list, usually with less than one message per day.

[1]: https://lists.libresoft.es/listinfo/metrics-grimoire

Contributing
------------

When making contributions, please follow the [PEP8 specification][2].
To check your code follows the specification, use a tool like
[pep8][3] or [flake8][4].

When adding new features, add tests for the new feature or fix, and check
that the existing tests pass.  Tests live in `pymlstats/tests` and you can
run them with:

```bash
$ python -m unittest discover
```

Please, also consider to add tests for the current features available.

[2]: http://www.python.org/dev/peps/pep-0008/
[3]: http://pypi.python.org/pypi/pep8
[4]: http://pypi.python.org/pypi/flake8/

Credits
-------

`mlstats` has been originally developed by the GSyC/LibreSoft group at
the Universidad Rey Juan Carlos in Mostoles, near Madrid (Spain). It is
part of a wider research on libre software engineering, aimed to gain
knowledge on how libre software is developed and maintained.


Main authors
------------

  * [Israel Herraiz]               <isra at herraiz org>
  * Jorge Gascon Perez             <jgascon at gsyc.escet.urjc.es>


Contributors
------------

  * [Dave Neary]                   <dneary at maemo org>
  * [Germán Poo-Caamaño]           <gpoo at gnome org>
  * [Luis Cañas]                   <lcanas at bitergia com>

  [Israel Herraiz]: http://herraiz.org/
  [Dave Neary]: http://blogs.gnome.org/bolsh/
  [Germán Poo-Caamaño]: http://calcifer.org/
  [Luis Cañas]: http://sanacl.wordpress.com/

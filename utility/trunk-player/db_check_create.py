#!/usr/bin/env python
# Check in DB exists, if not create it

import psycopg2
import sys
import os

con = None
error = None
database = os.environ.get("SQL_DATABASE")
db_user = os.environ.get("SQL_USER")
db_password = os.environ.get("SQL_PASSWORD")
db_host = os.environ.get("SQL_HOST")
db_port = os.environ.get("SQL_PORT")

try:
    con = psycopg2.connect(database=database, user=db_user,
        password=db_password, host=db_host, port=db_port)

    cur = con.cursor()

except psycopg2.DatabaseError as e:
    error = e

finally:

    if con:
        con.close()

if error is None:
    sys.exit(0)


print('Creating db')
con2 = None
try:
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    con2 = psycopg2.connect(user=db_user,
        password=db_password, host=db_host, port=db_port)
    con2.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);

    cur = con2.cursor()
    cur.execute('create database {};'.format(database))

except psycopg2.DatabaseError as e:
    print(f'Error {e}')
    sys.exit(1)

finally:

    if con2:
        con2.close()

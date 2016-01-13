import psycopg2
from psycopg2.extras import RealDictCursor
import json
import datetime
from app.util.util import Util

util = Util()

# Register a customized adapter for PostgreSQL decimal type
# to get a float instead of a decimal type
DEC2FLOAT = psycopg2.extensions.new_type(
  psycopg2.extensions.DECIMAL.values,
  'DEC2FLOAT',
  lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)

class Database:

  def sql_to_dict(self, sql, params=()):
    connection = None
    rows = None
    try:
      connection = psycopg2.connect("dbname='clb_dashboard' user='alex'")
      cursor = connection.cursor(cursor_factory=RealDictCursor)
      cursor.execute(sql, params)
      rows = cursor.fetchall()
    except psycopg2.DatabaseError, e:
      return None
    finally:
      if connection:
        connection.close()
      return rows

  def sql_to_json(self, sql, params=()):

    connection = None
    json_result = None
    try:
      connection = psycopg2.connect("dbname='clb_dashboard' user='alex'")
      cursor = connection.cursor(cursor_factory=RealDictCursor)
      cursor.execute(sql, params)
      rows = cursor.fetchall()

      json_result = []
      for r in rows:
        json_result.append(r)
      json_result = json.dumps(json_result, default=util.date_handler, indent=2)
    except psycopg2.DatabaseError, e:
      return None
    finally:
      if connection:
        connection.close()
      return json_result

  def sql_to_value(self, sql, params=()):
    connection = None
    scalar_result = None
    try:
      connection = psycopg2.connect("dbname='clb_dashboard' user='alex'")
      cursor = connection.cursor()
      cursor.execute(sql, params)
      scalar_result =  cursor.fetchone()
    except psycopg2.DatabaseError, e:
      return None
    finally:
      if connection:
        connection.close()
      return scalar_result

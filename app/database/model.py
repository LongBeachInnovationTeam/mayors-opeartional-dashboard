import psycopg2
from psycopg2.extras import RealDictCursor
import json
import datetime

date_handler = lambda obj: (
  obj.isoformat()
  if isinstance(obj, datetime.datetime)
  or isinstance(obj, datetime.date)
  else None
)

# Register a customized adapter for PostgreSQL decimal type
# to get a float instead of a decimal type
DEC2FLOAT = psycopg2.extensions.new_type(
  psycopg2.extensions.DECIMAL.values,
  'DEC2FLOAT',
  lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)

class Database:

  def sql_to_dict(self, sql):
    connection = None
    rows = None
    try:
      connection = psycopg2.connect("dbname='clb_dashboard' user='alex'")
      cursor = connection.cursor(cursor_factory=RealDictCursor)
      cursor.execute(sql)
      rows = cursor.fetchall()
    except psycopg2.DatabaseError, e:
      return None
    finally:
      if connection:
        connection.close()
      return rows

  def sql_to_json(self, sql):

    connection = None
    json_result = None
    try:
      connection = psycopg2.connect("dbname='clb_dashboard' user='alex'")
      cursor = connection.cursor(cursor_factory=RealDictCursor)
      cursor.execute(sql)
      rows = cursor.fetchall()

      json_result = []
      for r in rows:
        json_result.append(r)
      json_result = json.dumps(json_result, default=date_handler, indent=2)
    except psycopg2.DatabaseError, e:
      return None
    finally:
      if connection:
        connection.close()
      return json_result

  def sql_to_value(self, sql):
    connection = None
    scalar_result = None
    try:
      connection = psycopg2.connect("dbname='clb_dashboard' user='alex'")
      cursor = connection.cursor()
      cursor.execute(sql)
      scalar_result =  cursor.fetchone()
    except psycopg2.DatabaseError, e:
      return None
    finally:
      if connection:
        connection.close()
      return scalar_result

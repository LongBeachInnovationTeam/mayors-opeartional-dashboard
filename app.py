from flask import Flask
from flask import render_template
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import datetime

# Register a customized adapter for PostgreSQL decimal type
# to get a float instead of a decimal type
DEC2FLOAT = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMAL.values,
    'DEC2FLOAT',
    lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)

app = Flask(__name__)

date_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, datetime.datetime)
    or isinstance(obj, datetime.date)
    else None
)

def sql_to_dict(sql):
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

def sql_to_json(sql):
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

def sql_to_value(sql):
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

@app.route('/')
def index():
    sql = """
        SELECT      location
                    ,topic
                    ,COUNT(topic) as topic_count
        FROM        go_long_beach
        WHERE       status = 'Open' OR status = 'Pending'
        GROUP BY    location, topic
        ORDER BY    topic_count DESC
        LIMIT 10;
    """
    result = sql_to_dict(sql)
    return render_template("index.html", multiple_locations=result)

@app.route('/data/go_lb/last_updated')
def go_lb_last_updated():
    sql = """
        SELECT MAX(GREATEST(entered_date, date_closed, date_last_updated))
        FROM go_long_beach;
    """
    last_updated = sql_to_value(sql)
    return json.dumps(last_updated, default=date_handler)

@app.route('/data/go_lb/measures')
def go_lb_avg_days_to_close():

    # Compute the total number of requests
    sql = """
        SELECT  COUNT(*)
        FROM    go_long_beach;
    """
    requests_count = sql_to_value(sql)

    # Compute the total number of Open requests
    sql = """
        SELECT  COUNT(*)
        FROM    go_long_beach
        WHERE   status = 'Open';
    """
    open_requests_count = sql_to_value(sql)

    # Compute the total number of Pending requests
    sql = """
        SELECT  COUNT(*)
        FROM    go_long_beach
        WHERE   status = 'Pending';
    """
    pending_requests_count = sql_to_value(sql)

    # Compute the total number of Closed requests
    sql = """
        SELECT  COUNT(*)
        FROM    go_long_beach
        WHERE   status = 'Closed';
    """
    closed_requests_count = sql_to_value(sql)

    # Compute the average amount of days to close a request
    sql = """
        SELECT ROUND(AVG(date_closed - entered_date)::numeric, 2) AS avg_days_to_close
        FROM go_long_beach;
    """
    avg_days_to_close = sql_to_value(sql)

    # Create a dictionary of measures to return to the users
    measures = {
        'avgDaysToClose': avg_days_to_close,
        'totalRequests': requests_count,
        'openRequests': open_requests_count,
        'pendingRequests': pending_requests_count,
        'closedRequests': closed_requests_count
    }

    return json.dumps(measures)

@app.route('/data/go_lb/departments')
def go_lb_departments():
    sql = """
        SELECT department, COUNT(request) AS count
        FROM go_long_beach
        WHERE entered_date BETWEEN '2015-10-01' AND '2015-10-31'
        GROUP BY department
        ORDER BY count DESC;
    """
    return sql_to_json(sql)

@app.route('/data/go_lb/topics')
def go_lb_topics():
    sql = """
        SELECT topic, COUNT(request) AS count
        FROM go_long_beach
        WHERE entered_date BETWEEN '2015-10-01' AND '2015-10-31'
        GROUP BY topic
        ORDER BY count ASC;
    """
    return sql_to_json(sql)

@app.route('/data/go_lb/map')
def go_lb_map():
    sql = """
        SELECT request
            , topic
            , priority
            , split_part(location_coordinates, ',', 1) AS latitude
            , split_part(location_coordinates, ',', 2) as longitude
        FROM go_long_beach;
    """
    return sql_to_json(sql)

@app.route('/data/go_lb/repeat_requests')
def go_lb_repeat_requests():
    sql = """
        SELECT      location
                    ,topic
                    ,COUNT(topic) as topic_count
        FROM        go_long_beach
        WHERE       (entered_date BETWEEN '2015-10-01' AND '2015-10-31')
        GROUP BY    location, topic
        ORDER BY    topic_count DESC;
    """
    return sql_to_dict(sql)

@app.route('/data/go_lb/status_ytd')
def go_lb_status_ytd():
    sql = """
        SELECT      status
                    ,COUNT(*) AS record_count
                    ,date_trunc('month', entered_date) AS reporting_date
        FROM        go_long_beach
        WHERE       status = 'Open' or status = 'Closed'
        GROUP BY    status, date_trunc('month', entered_date);
    """
    return sql_to_json(sql)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=1337,debug=True)
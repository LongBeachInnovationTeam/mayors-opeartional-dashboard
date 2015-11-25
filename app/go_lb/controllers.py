from flask import Blueprint, render_template
from app.database.model import Database
import json

db = Database()

go_lb = Blueprint('go_lb', __name__, url_prefix='/')

# TO-DO: Re-factor with date_handler from the database module
date_handler = lambda obj: (
  obj.isoformat()
  if isinstance(obj, datetime.datetime)
  or isinstance(obj, datetime.date)
  else None
)

@go_lb.route('/')
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
  result = db.sql_to_dict(sql)
  return render_template('go_lb/index.html', multiple_locations=result)

@go_lb.route('data/go_lb/last_updated')
def go_lb_last_updated():
  sql = """
    SELECT MAX(GREATEST(entered_date, date_closed, date_last_updated))
    FROM go_long_beach;
  """
  last_updated = db.sql_to_value(sql)
  return json.dumps(last_updated, default=date_handler)

@go_lb.route('data/go_lb/measures')
def go_lb_avg_days_to_close():

  # Compute the total number of requests
  sql = """
    SELECT  COUNT(*)
    FROM    go_long_beach;
  """
  requests_count = db.sql_to_value(sql)

  # Compute the total number of Open requests
  sql = """
    SELECT  COUNT(*)
    FROM    go_long_beach
    WHERE   status = 'Open';
  """
  open_requests_count = db.sql_to_value(sql)

  # Compute the total number of Pending requests
  sql = """
    SELECT  COUNT(*)
    FROM    go_long_beach
    WHERE   status = 'Pending';
  """
  pending_requests_count = db.sql_to_value(sql)

  # Compute the total number of Closed requests
  sql = """
    SELECT  COUNT(*)
    FROM    go_long_beach
    WHERE   status = 'Closed';
  """
  closed_requests_count = db.sql_to_value(sql)

  # Compute the average amount of days to close a request
  sql = """
    SELECT ROUND(AVG(date_closed - entered_date)::numeric, 2) AS avg_days_to_close
    FROM go_long_beach;
  """
  avg_days_to_close = db.sql_to_value(sql)

  # Create a dictionary of measures to return to the users
  measures = {
    'avgDaysToClose': avg_days_to_close,
    'totalRequests': requests_count,
    'openRequests': open_requests_count,
    'pendingRequests': pending_requests_count,
    'closedRequests': closed_requests_count
  }

  return json.dumps(measures)

@go_lb.route('data/go_lb/departments')
def go_lb_departments():
  sql = """
    SELECT 		department, COUNT(request) AS count
    FROM 			go_long_beach
    WHERE			entered_date BETWEEN '2015-10-01' AND '2015-10-31'
    GROUP BY	department
    ORDER BY	count DESC;
  """
  return db.sql_to_json(sql)

@go_lb.route('data/go_lb/topics')
def go_lb_topics():
  sql = """
    SELECT 		topic, COUNT(request) AS count
    FROM 			go_long_beach
    WHERE 		entered_date BETWEEN '2015-10-01' AND '2015-10-31'
    GROUP BY 	topic
    ORDER BY	count ASC;
  """
  return db.sql_to_json(sql)

@go_lb.route('data/go_lb/map')
def go_lb_map():
  sql = """
    SELECT	request
	        	, topic
	        	, priority
	        	, split_part(location_coordinates, ',', 1) AS latitude
	        	, split_part(location_coordinates, ',', 2) as longitude
    FROM 		go_long_beach;
  """
  return db.sql_to_json(sql)

@go_lb.route('data/go_lb/repeat_requests')
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
  return db.sql_to_dict(sql)

@go_lb.route('data/go_lb/status_ytd')
def go_lb_status_ytd():
  sql = """
    SELECT      status
                ,COUNT(*) AS record_count
                ,date_trunc('month', entered_date) AS reporting_date
    FROM        go_long_beach
    WHERE       status = 'Open' or status = 'Closed'
    GROUP BY    status, date_trunc('month', entered_date);
  """
  return db.sql_to_json(sql)

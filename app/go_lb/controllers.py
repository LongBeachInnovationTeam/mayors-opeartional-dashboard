from flask import Blueprint, render_template
from app.database.model import Database
import collections, datetime, json

db = Database()

go_lb = Blueprint('go_lb', __name__)

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
  duplicate_locations = db.sql_to_dict(sql)

  sql = """
    SELECT    department
              ,ROUND(AVG(date_closed - entered_date)::numeric, 2) AS avg_days_to_close
    FROM      go_long_beach
    WHERE     date_closed - entered_date IS NOT NULL AND entered_date BETWEEN '2015-10-01' AND '2015-10-31'
    GROUP BY  department
    ORDER BY  avg_days_to_close DESC;
  """
  department_averages = db.sql_to_dict(sql)

  result = {
    'duplicate_locations': duplicate_locations,
    'department_averages': department_averages
  }

  return render_template('go_lb/index.html', table_data=result)

@go_lb.route('/go_lb/drilldown')
def go_lb_drilldown():
  return render_template('go_lb/drilldown.html')

@go_lb.route('/data/go_lb/last_updated')
def go_lb_last_updated():
  sql = """
    SELECT MAX(GREATEST(entered_date, date_closed, date_last_updated))
    FROM go_long_beach;
  """
  last_updated = db.sql_to_value(sql)
  return json.dumps(last_updated, default=date_handler)

@go_lb.route('/data/go_lb/topics')
def go_lb_topics():
  sql = """
    SELECT    topic, COUNT(request) AS count
    FROM      go_long_beach
    WHERE     entered_date BETWEEN '2015-10-01' AND '2015-10-31'
    GROUP BY  topic
    ORDER BY  count ASC;
  """
  return db.sql_to_json(sql)

@go_lb.route('/data/go_lb/measures')
def go_lb_measures():

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

  sql = """
    SELECT    date_trunc('month', entered_date) AS reporting_month
              ,COUNT(*) AS request_count
    FROM      go_long_beach
    WHERE     status = 'Open'
    GROUP BY  status, reporting_month
    ORDER BY  reporting_month;
  """
  open_requests_ytd = db.sql_to_dict(sql)

  sql = """
    SELECT    date_trunc('month', entered_date) AS reporting_month
              ,COUNT(*) AS request_count
    FROM      go_long_beach
    WHERE     status = 'Pending'
    GROUP BY  status, reporting_month
    ORDER BY  reporting_month;
  """
  pending_requests_ytd = db.sql_to_dict(sql)

  sql = """
    SELECT    date_trunc('month', entered_date) AS reporting_month
              ,COUNT(*) AS request_count
    FROM      go_long_beach
    WHERE     status = 'Closed'
    GROUP BY  status, reporting_month
    ORDER BY  reporting_month;
  """
  closed_requests_ytd = db.sql_to_dict(sql)

  sql = """
    SELECT    date_trunc('month', entered_date) AS reporting_month
              ,ROUND(AVG(date_closed - entered_date)::numeric, 2) AS avg_days_to_close
    FROM      go_long_beach
    GROUP BY  reporting_month
    ORDER BY  reporting_month;
  """
  average_requests_close_ytd = db.sql_to_dict(sql)

  # Create a dictionary of measures to return to the users
  # This populates the stat cards (numbers)
  measures = {
    'avgDaysToClose': avg_days_to_close,
    'totalRequests': requests_count,
    'openRequests': open_requests_count,
    'pendingRequests': pending_requests_count,
    'closedRequests': closed_requests_count
  }

  # Data will be used to render the sparkline chart
  # under each measure
  measures_charts = {
    'openRequests': open_requests_ytd,
    'pendingRequests': pending_requests_ytd,
    'closedRequests': closed_requests_ytd,
    'averageRequests': average_requests_close_ytd
  }

  # This will be converted into the JSON
  # document that the client will consumer
  # via XHR or AJAX request
  result = {
    'measures': measures,
    'measures_charts': measures_charts
  }

  return json.dumps(result, default=date_handler)

@go_lb.route('/data/go_lb/map')
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

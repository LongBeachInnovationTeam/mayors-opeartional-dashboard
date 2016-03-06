from flask import Blueprint, render_template
from app.database.model import Database
from app.util.util import Util
from collections import Counter
import collections, datetime, json

db = Database()
util = Util()

go_lb = Blueprint('go_lb', __name__)

today = datetime.date.today()
reporting_dates = {
  'today': today.isoformat(),
  'yesterday': today.replace(day = today.day - 1).isoformat(),
  'tomorrow': today.replace(day = today.day + 1).isoformat(),
  'cur_year_start': str(today.year) + '-01-01',
  'cur_year_end': str(today.year) + '-12-31',
  'cur_month_start': util.get_month_day_range(today)[0].isoformat(),
  'cur_month_end': util.get_month_day_range(today)[1].isoformat(),
  'cur_week_start': util.get_week_day_range(today)[0].isoformat(),
  'cur_week_end': util.get_week_day_range(today)[6].isoformat()
}

def get_reporting_period_interval(date_reporting_type):
  if date_reporting_type == 'ytd':
    return (reporting_dates['cur_year_start'], reporting_dates['cur_year_end'])
  elif date_reporting_type == 'month':
    return (reporting_dates['cur_month_start'], reporting_dates['cur_month_end'])
  elif date_reporting_type == 'week':
    return (reporting_dates['cur_week_start'], reporting_dates['cur_week_end'])
  else:
    return (reporting_dates['today'], reporting_dates['today'])

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

  # sql = """
  #   SELECT    department
  #             ,ROUND(AVG(date_closed - entered_date)::numeric, 2) AS avg_days_to_close
  #   FROM      go_long_beach
  #   WHERE     date_closed - entered_date IS NOT NULL AND entered_date BETWEEN '2015-10-01' AND '2015-10-31'
  #   GROUP BY  department
  #   ORDER BY  avg_days_to_close DESC;
  # """
  # department_averages = db.sql_to_dict(sql)

  # department_average_values = []
  # for dept in department_averages:
  #   avg = dept['avg_days_to_close']
  #   department_average_values.append(avg)

  # min_avg = min(department_average_values)
  # max_avg = max(department_average_values)
  # for dept in department_averages:
  #   avg = dept['avg_days_to_close']
  #   dept['normalized_avg'] = round((float(avg - min_avg)) / (float(max_avg - min_avg)), 2)

  # sql = """
  #   SELECT    department
  #             ,COUNT(request) AS count
  #   FROM      go_long_beach
  #   WHERE     entered_date BETWEEN '2015-10-01' AND '2015-10-31'
  #   GROUP BY  department
  #   ORDER BY  count DESC;
  # """
  # department_count = db.sql_to_dict(sql)

  # department_count_values = []
  # for dept in department_count:
  #   count = dept['count']
  #   department_count_values.append(count)

  # min_count = min(department_count_values)
  # max_count = max(department_count_values)
  # for dept in department_count:
  #   count = dept['count']
  #   dept['normalized_count'] = round((float(count - min_count)) / (float(max_count - min_count)), 2)

  result = {
    'duplicate_locations': duplicate_locations
    # 'department_averages': department_averages,
    # 'department_count': department_count
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
  return json.dumps(last_updated, default=util.date_handler)

def clean_description(desc):
  desc = desc.lower()
  desc = desc.strip()
  return desc

def count_words(desc):
  desc = clean_description(desc)
  return dict(Counter(desc.split()))

@go_lb.route('/data/go_lb/word_cloud')
def go_lb_word_cloud():
  sql = """
    SELECT  string_agg(description, ' ') AS description_text
    FROM    go_long_beach
    WHERE   entered_date BETWEEN %s AND %s;
  """
  params = (reporting_dates['cur_month_start'], reporting_dates['cur_month_end'])
  description = db.sql_to_value(sql, params)
  word_count_dict = count_words(description[0])
  return json.dumps(word_count_dict, util.date_handler)

@go_lb.route('/data/go_lb/topics')
def go_lb_topics():
  sql = """
    SELECT    topic, COUNT(request) AS count
    FROM      go_long_beach
    WHERE     entered_date BETWEEN %s AND %s
    GROUP BY  topic
    ORDER BY  count ASC;
  """
  params = (reporting_dates['cur_month_start'], reporting_dates['cur_month_end'])
  topics_count = db.sql_to_dict(sql, params)

  sql = """
    SELECT    topic
              ,ROUND(AVG(date_closed - entered_date)::numeric, 2) AS avg_days_to_close
    FROM      go_long_beach
    WHERE     (date_closed - entered_date IS NOT NULL) AND (entered_date BETWEEN %s AND %s)
    GROUP BY  topic
    ORDER BY  avg_days_to_close;
  """
  params = (reporting_dates['cur_month_start'], reporting_dates['cur_month_end'])
  topics_average = db.sql_to_dict(sql, params)

  results = {
    "topics_count": topics_count,
    "topics_average": topics_average
  }

  return json.dumps(results, default=util.date_handler)

@go_lb.route('/data/go_lb/departments')
def go_lb_departments():
  sql = """
    SELECT    department
              ,COUNT(request) AS requests_count
              ,ROUND(AVG(date_closed - entered_date)::numeric, 2) AS avg_days_to_close
    FROM      go_long_beach
    WHERE     (date_closed - entered_date IS NOT NULL) AND (entered_date BETWEEN %s AND %s)
    GROUP BY  department
    ORDER BY  avg_days_to_close DESC;
  """
  params = (reporting_dates['cur_month_start'], reporting_dates['cur_month_end'])
  result = db.sql_to_dict(sql, params)

  department_rename_mapper = {
    'Technology & Innovation': 'TID',
    'City Light and Power': 'Light/Power',
    'Animal Care Services Bureau': 'ACS',
    'Parks and Rec and Marine': 'PRM',
    'Public Works': 'PW',
    'PW - Engineering': 'PW Engr',
    'Traffic Engineering': 'Traffic',
    'Development Services': 'DS'
  }
  for r in result:
    r['department_display_name'] = department_rename_mapper[r['department']]

  return json.dumps(result)

@go_lb.route('/data/go_lb/measures')
def go_lb_measures():

  # TO-DO: Get params by selected date button
  params = (reporting_dates['cur_month_start'], reporting_dates['cur_month_end'])

  # Compute the total number of requests
  sql = """
    SELECT  COUNT(*)
    FROM    go_long_beach
    WHERE   entered_date BETWEEN %s AND %s
  """
  requests_count = db.sql_to_value(sql, params)

  # Compute the total number of Open requests
  sql = """
    SELECT  COUNT(*)
    FROM    go_long_beach
    WHERE   (entered_date BETWEEN %s AND %s) AND (status = 'Open');
  """
  open_requests_count = db.sql_to_value(sql, params)

  # Compute the total number of Pending requests
  sql = """
    SELECT  COUNT(*)
    FROM    go_long_beach
    WHERE   (entered_date BETWEEN %s AND %s) AND (status = 'Pending');
  """
  pending_requests_count = db.sql_to_value(sql, params)

  # Compute the total number of Closed requests
  sql = """
    SELECT  COUNT(*)
    FROM    go_long_beach
    WHERE   (entered_date BETWEEN %s AND %s) AND (status = 'Closed');
  """
  closed_requests_count = db.sql_to_value(sql, params)

  # Compute the average amount of days to close a request
  sql = """
    SELECT    ROUND(AVG(date_closed - entered_date)::numeric, 2) AS avg_days_to_close
    FROM      go_long_beach
    WHERE     entered_date BETWEEN %s AND %s;
  """
  avg_days_to_close = db.sql_to_value(sql, params)

  sql = """
    SELECT    entered_date AS reporting_date
              ,COUNT(*) AS request_count
    FROM      go_long_beach
    WHERE     (entered_date BETWEEN %s AND %s) AND (status = 'Open')
    GROUP BY  status, reporting_date
    ORDER BY  reporting_date;
  """
  open_requests_ytd = db.sql_to_dict(sql, params)

  sql = """
    SELECT    entered_date AS reporting_date
              ,COUNT(*) AS request_count
    FROM      go_long_beach
    WHERE     (entered_date BETWEEN %s AND %s) AND (status = 'Pending')
    GROUP BY  status, reporting_date
    ORDER BY  reporting_date;
  """
  pending_requests_ytd = db.sql_to_dict(sql, params)

  sql = """
    SELECT    entered_date AS reporting_date
              ,COUNT(*) AS request_count
    FROM      go_long_beach
    WHERE     (entered_date BETWEEN %s AND %s) AND (status = 'Closed')
    GROUP BY  status, reporting_date
    ORDER BY  reporting_date;
  """
  closed_requests_ytd = db.sql_to_dict(sql, params)

  sql = """
    SELECT    entered_date AS reporting_date
              ,ROUND(AVG(date_closed - entered_date)::numeric, 2) AS avg_days_to_close
    FROM      go_long_beach
    WHERE     entered_date BETWEEN %s AND %s
    GROUP BY  reporting_date
    ORDER BY  reporting_date;
  """
  average_requests_close_ytd = db.sql_to_dict(sql, params)

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

  return json.dumps(result, default=util.date_handler)

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

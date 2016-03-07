import datetime, calendar

class ReportingCalendar:

	def __init__(self):
		today = datetime.date.today()
		self.reporting_dates = {
		  'today': today.isoformat(),
		  'yesterday': today.replace(day = today.day - 1).isoformat(),
		  'tomorrow': today.replace(day = today.day + 1).isoformat(),
		  'cur_year_start': str(today.year) + '-01-01',
		  'cur_year_end': str(today.year) + '-12-31',
		  'cur_month_start': self.get_month_day_range(today)[0].isoformat(),
		  'cur_month_end': self.get_month_day_range(today)[1].isoformat(),
		  'cur_week_start': self.get_week_day_range(today)[0].isoformat(),
		  'cur_week_end': self.get_week_day_range(today)[6].isoformat()
		}

	def get_reporting_period_interval(self, date_reporting_type):
	  if date_reporting_type == 'ytd':
	    return (self.reporting_dates['cur_year_start'], self.reporting_dates['cur_year_end'])
	  elif date_reporting_type == 'month':
	    return (self.reporting_dates['cur_month_start'], self.reporting_dates['cur_month_end'])
	  elif date_reporting_type == 'week':
	    return (self.reporting_dates['cur_week_start'], self.reporting_dates['cur_week_end'])
	  elif date_reporting_type == 'today':
	    return (self.reporting_dates['today'], self.reporting_dates['today'])

	def get_week_day_range(self, date):
		return [date + datetime.timedelta(days=i) for i in range(0 - date.weekday(), 7 - date.weekday())]

	def get_month_day_range(self, date):
	  """
	  For a date 'date' returns the start and end date for the month of 'date'.

	  Month with 31 days:
	  >>> date = datetime.date(2011, 7, 27)
	  >>> get_month_day_range(date)
	  (datetime.date(2011, 7, 1), datetime.date(2011, 7, 31))

	  Month with 28 days:
	  >>> date = datetime.date(2011, 2, 15)
	  >>> get_month_day_range(date)
	  (datetime.date(2011, 2, 1), datetime.date(2011, 2, 28))
	  """
	  first_day = date.replace(day = 1)
	  last_day = date.replace(day = calendar.monthrange(date.year, date.month)[1])
	  return first_day, last_day
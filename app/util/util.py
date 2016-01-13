import datetime
import calendar

class Util:

	date_handler = lambda self, obj: (
	  obj.isoformat()
	  if isinstance(obj, datetime.datetime)
	  or isinstance(obj, datetime.date)
	  else None
	)

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
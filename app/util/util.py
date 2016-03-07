from app.util.reporting_calendar import ReportingCalendar
import datetime

class Util:

	def __init__(self):
		self.reporting_calendar = ReportingCalendar()
		self.date_handler = lambda obj: (
		  obj.isoformat()
		  if isinstance(obj, datetime.datetime)
		  or isinstance(obj, datetime.date)
		  else None
		)

from datetime import date as datetime_date

class BalanceSheet(object):
    """Main balance sheet class"""
    def __init__(self, date=None):
        if date is None:
            date = datetime_date.today()
        try:
            date = datetime_date(*date)
        except:
            pass
        self.date = date

    def __repr__(self):
        return '<%s date="%s">' % (self.__class__.__name__, self.date.isoformat())

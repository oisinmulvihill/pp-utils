'''
Dates and Times module

Created on Oct 18, 2012

@author: eeaston
'''
import time
from datetime import timedelta

import dateutil.parser

CLOSED_CLOSED = 0
CLOSED_OPEN = 1
OPEN_CLOSED = 2
OPEN_OPEN = 3


class TimeReference(object):
    """ Represents a piece of data referring to date or time
        Eg:
           A date range:   (start='2013-08-14',
                            end='2013-08-15', interval=CLOSED_CLOSED)
           A point in time:  '2013-08-14 18:00'
           A fuzzy match:  'Tuesday afternoon'
           A range of dates: 'Weekly on Tuesday at 18:00'
    """
    def __init__(self):
        pass

    # TODO: find a way to use 'in', eg 'if dt in timeref..'
    #       Look @ pkg_resources version parser
    def match(self, dt):
        """ True if a given datetime matches the time reference
        """
        raise NotImplemented


class PointInTime(TimeReference):
    def __init__(self, point):
        self.point = dateutil.parser.parse(point)


class FuzzyTimeReference(TimeReference):
    pass


class Duration(TimeReference):
    def __init__(self, minutes=None, hours=None, days=None):
        self.duration = (((days or 0) * 24 * 60) + ((hours or 0) * 60) +
                         (minutes or 0))


class RepeatingTimeReference(TimeReference):
    def __init__(self, start_at, duration, period,
                 stop_at=None):
        self.start_at = start_at
        self.stop_at = stop_at
        self.duration = duration
        self.period = period


# TODO: think about relative dates (datutil.relativedelta)
class DateRange(TimeReference):
    """
    Date range representation.
    """
    def __init__(self, start=None, end=None, interval=CLOSED_OPEN):
        self.start = dateutil.parser.parse(start) if start else None
        self.end = dateutil.parser.parse(end) if end else None
        self.interval = interval

    def __repr__(self):
        return "<DateRange {}--{}>".format(self.start, self.end)

    def to_dict(self):
        """Convert to a JSON representation of this instance.

        :returns: A dict

        E.g.::
            {
                "interval": <interval value>,
                "start": <ISO Format> or "",
                "end": <ISO Format> or "",
            }

        """
        start = self.start.isoformat() if self.start else ""

        end = self.end.isoformat() if self.end else ""

        return dict(
            interval=self.interval,
            start=start,
            end=end,
        )

    def minutes(self):
        """
        Number of full minutes in this date range
        """
        return int((self.end - self.start).seconds) / 60

    def match(self, dt):
        """ True if this datetime is contained within this date range
        """
        logic_map = {
            CLOSED_CLOSED: ((self.start is None or dt >= self.start) and
                            (self.end is None or dt <= self.end)),
            CLOSED_OPEN: ((self.start is None or dt >= self.start) and
                          (self.end is None or dt < self.end)),
            OPEN_CLOSED: ((self.start is None or dt > self.start) and
                          (self.end is None or dt <= self.end)),
            OPEN_OPEN: ((self.start is None or dt > self.start) and
                        (self.end is None or dt < self.end)),
        }
        return logic_map[self.interval]

    __slots__ = ['start', 'end', 'interval']


def next_recurrance(start_date, frequency, dt):
    """ Returns the next recurrence of a recurring slot after a given datetime

    Parameters
    ----------
    start_date: `datetime`
        Series start
    frequency: int
        Recurrence frequency in minutes
    dt: `datetime`
        Datetime after which we want the next recurrence

    """
    seconds_since_seq_start = (time.mktime(dt.timetuple()) -
                               time.mktime(start_date.timetuple()))
    return (start_date +
            timedelta(seconds=(seconds_since_seq_start % (frequency * 60))))

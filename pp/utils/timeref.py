'''
Dates and Times module

Created on Oct 18, 2012

@author: eeaston
'''
import time
from datetime import timedelta, datetime

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

    def dt(self, thing):
        if thing:
            if isinstance(thing, datetime):
                return thing
            return dateutil.parser.parse(thing)
        return None

    @classmethod
    def fromJSON(cls, data):
        """ Convert from JSON dict to an instance
        """
        return SERIALISE_CLASS_LOOKUP[data['timeref_type']].fromJSON(data)


class PointInTime(TimeReference):
    def __init__(self, point):
        self.point = self.dt(point)


class FuzzyTimeReference(TimeReference):
    pass


class Duration(TimeReference):
    def __init__(self, minutes=None, hours=None, days=None):
        self.minutes = (((days or 0) * 24 * 60) + ((hours or 0) * 60) +
                         (minutes or 0))


class RepeatingTimeReference(TimeReference):
    def __init__(self, start, frequency,
                 end_after_time=None, end_after_repeat=None):
        """ Repeating series of times or time slots.

        Parameters
        ----------
        start: `TimeReference`
            Series start
        frequency: int
            Recurrence frequency in minutes
        end_after_time: `TimeRef`
            Series ends after this time reference
        end_after_repeat: `int`
            Series ends after this many recurrences
        """
        self.start = start
        self.frequency = frequency
        self.end_after_time = end_after_time
        self.end_after_repeat = end_after_repeat

    def next_after(self, dt):
        """ Returns the next recurrence of the series after a given datetime

        Parameters
        ----------
        dt: `datetime`
            Datetime after which we want the next recurrence

        Explanation::

            [start_date .... r0 ...... r1 ...... rn-1 .. dt .. rn]
                             [ f = freq ]                       ^
            [ ---- s = seconds since seq start ----------]      |
                                                 [ s % f ]      |
                                                                |
                                                       rn = dt + f - (s % f)
        """
        if dt < self.start:
            return self.start
        if self.end_after_time and dt > self.end_after_time:
            return None
        f = self.frequency * 60
        s = (time.mktime(dt.timetuple()) -
             time.mktime(self.start.timetuple()))
        if self.end_after_repeat and (s - s % f) / f >= self.end_after_repeat:
            return None
        return dt + timedelta(seconds=f - s % f)


# TODO: think about relative dates (datutil.relativedelta)
class DateRange(TimeReference):
    """
    Date range representation.
    """
    def __init__(self, start=None, end=None, interval=CLOSED_OPEN):
        self.start = self.dt(start)
        self.end = self.dt(end)
        self.interval = interval

    def __repr__(self):
        return "<DateRange {}--{}>".format(self.start, self.end)

    def __eq__(self, other):
        return (self.start == other.start and
                self.end == other.end and
                self.interval == other.interval)

    def __json__(self, request=None):
        """Convert to a JSON representation of this instance.

        Returns
        -------
        A natively json-serializable object

        E.g.::
            {
                "interval": <interval value>,
                "start": <ISO Format> or None,
                "end": <ISO Format> or None,
            }

        """
        # start = self.start.isoformat() if self.start else None
        # end = self.end.isoformat() if self.end else None
        return dict(
            timeref_type="daterange",
            interval=self.interval,
            start=self.start,
            end=self.end,
        )

    @classmethod
    def fromJSON(cls, data):
        """ Convert from JSON dict to an instance
        """
        return cls(start=data['start'],
                   end=data['end'],
                   interval=data['interval'])

    @property
    def minutes(self):
        """
        Number of full minutes in this date range
        """
        return int((self.end - self.start).total_seconds()) / 60

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


SERIALISE_CLASS_LOOKUP = {
    'daterange': DateRange,
}

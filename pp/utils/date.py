'''
Dates and Times module

Created on Oct 18, 2012

@author: eeaston
'''
import dateutil.parser

CLOSED_CLOSED = 0
CLOSED_OPEN = 1
OPEN_CLOSED = 2
OPEN_OPEN = 3


class DateRange(object):
    """
    Date range representation.
    """
    def __init__(self, start=None, end=None, interval=CLOSED_OPEN):
        self.start = dateutil.parser.parse(start) if start else None
        self.end = dateutil.parser.parse(end) if end else None
        self.interval = interval

    def __repr__(self):
        return "<DateRange {}--{}>".format(self.start, self.end)

    __slots__ = ['start', 'end', 'interval']

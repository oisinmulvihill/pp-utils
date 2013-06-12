'''
Common Formencode utils

Created on Jun 3, 2013

@author: Edward Easton
'''
import uuid

from dateutil.parser import parse
from formencode import validators
from formencode.api import FancyValidator

import timeref


class StringID(FancyValidator):
    """Used to validate a _id db fields or provide a default if on isn't.
    """
    def __init__(self, prefix="", *args, **kwargs):
        self.prefix = prefix
        kwargs['not_empty'] = False
        kwargs['if_missing'] = self.newid()
        super(StringID, self).__init__(*args, **kwargs)

    def newid(self):
        docid = "{:s}".format(uuid.uuid4())
        docid = docid.replace("-", "")
        return "{:s}-{:s}".format(self.prefix, docid)

    def _to_python(self, value, state):
        if value:
            value = value.lower().strip()
        else:
            value = self.newid()
        return value


class DateTime(FancyValidator):
    """Convert strings to datetime instances using python-dateutil parse.
    """
    def _to_python(self, value, state):
        if isinstance(value, basestring):
            value = parse(value)
            value = value.isoformat()

        return value


class TimeRef(FancyValidator):
    accept_iterator = True

    def _to_python(self, value, state):
        if isinstance(value, dict):
            return timeref.TimeReference.fromJSON(value)
        return value

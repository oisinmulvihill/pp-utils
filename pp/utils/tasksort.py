# -*- coding: utf-8 -*-
# pp/utils/tasksort.py


class Task(object):

    urgency_dict = {
        "sometime": 1,
        "this-week": 2,
        "today": 5
    }

    def __init__(self, status=None, urgency=None):
        self.status = status
        self.urgency = urgency

    @property
    def priority(self):
        return self.urgency_dict[self.urgency]


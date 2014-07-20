# -*- coding: utf-8 -*-
# pp/utils/test_tasksort.py

from datetime import datetime
from dateutil.parser import parse as dt
from pprint import pprint

import pytest
import mock

from pp.utils.optionlines import OptionLines

@pytest.mark.xfail
def test_sort_tasks_by_urgency123():
    source_text = """\
* [ ] Sometime 2
**[ ] Today 1
* [ ] Sometime 1
  [ ] This week 2
**[ ] Today 2
  [ ] This week 1
* [ ] Sometime 3
"""
    option_lines = OptionLines(source_text)
    assert len(option_lines) == 7
    assert 0 == 56


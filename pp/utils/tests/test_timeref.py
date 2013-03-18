# -*- coding: utf-8 -*-
from datetime import datetime as dt

import pytest

from pp.utils.timeref import DateRange, next_recurrance


def test_daterange_constructor_empty():
    dr = DateRange()
    assert dr.start is None
    assert dr.end is None


def test_daterange_constructor_partial():
    dr = DateRange('20100908')
    assert dr.start == dt(2010, 9, 8)
    assert dr.end is None


def test_daterange_constructor():
    dr = DateRange('20100908', '20111009')
    assert dr.start == dt(2010, 9, 8)
    assert dr.end == dt(2011, 10, 9)


@pytest.mark.xfail
@pytest.mark.parametrize(('start_date', 'freq', 'dt', 'expected'), [
    (dt("2013-01-01 09:00"), 10, dt("2013-01-01 09:53"),
     dt("2013-01-01 10:00")),
])
def test_next_recurrance(start_date, freq, dt, expected):
    assert next_recurrance(start_date, freq, dt) == expected


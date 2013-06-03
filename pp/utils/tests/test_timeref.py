# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil.parser import parse as dt
import pytest

from pp.utils.timeref import DateRange, RepeatingTimeReference


def test_daterange_constructor_empty():
    dr = DateRange()
    assert dr.start is None
    assert dr.end is None


def test_daterange_constructor_partial():
    dr = DateRange('20100908')
    assert dr.start == datetime(2010, 9, 8)
    assert dr.end is None


def test_daterange_constructor():
    dr = DateRange('20100908', '20111009')
    assert dr.start == datetime(2010, 9, 8)
    assert dr.end == datetime(2011, 10, 9)


def test_daterange_minutes():
    dr = DateRange('20010101', '20010102')
    assert dr.minutes == 60 * 24


def test_daterange_minutes_zero():
    dr = DateRange('20010101', '20010101')
    assert dr.minutes == 0


def test_daterange_minutes_negative():
    dr = DateRange('20010102', '20010101')
    assert dr.minutes == -60 * 24


@pytest.mark.parametrize(('start_date', 'freq', 'dt', 'expected'), [
    # 10 min freq
    (dt("2013-01-01 09:00"), 10, dt("2013-01-01 09:53"),
     dt("2013-01-01 10:00")),
    # 5 min freq
    (dt("2013-01-01 09:00"), 5, dt("2013-01-01 09:53"),
     dt("2013-01-01 09:55")),
    # Next day
    (dt("2013-01-01 09:00"), 60 * 24, dt("2013-01-01 09:53"),
     dt("2013-01-02 09:00")),
    # Before series start
    (dt("2013-01-01 09:00"), 60 * 24, dt("2012-01-01 09:45"),
     dt("2013-01-01 09:00")),
])
def test_repeating(start_date, freq, dt, expected):
    assert RepeatingTimeReference(start_date, freq).next_after(dt) == expected


def test_repeating_end_after_time():
    rr = RepeatingTimeReference(start=dt("2013-01-01 09:00"),
                                frequency=10,
                                end_after_time=dt("2013-01-01 10:00"))
    assert rr.next_after(dt("2013-01-02 10:00")) is None


def test_repeating_end_after_repeat():
    rr = RepeatingTimeReference(start=dt("2013-01-01 09:00"),
                                frequency=10,
                                end_after_repeat=2)
    assert rr.next_after(dt("2013-01-01 09:19")) == dt("2013-01-01 09:20")
    assert rr.next_after(dt("2013-01-01 09:20")) is None
    assert rr.next_after(dt("2013-01-01 09:21")) is None


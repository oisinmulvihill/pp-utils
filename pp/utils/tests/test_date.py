# -*- coding: utf-8 -*-
from datetime import datetime as dt

from pp.utils.date import DateRange


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

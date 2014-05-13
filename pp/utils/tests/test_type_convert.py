# -*- coding: utf-8 -*-
# pp-utils/pp/utils/tests/test_type_convert.py

import pytest

from pp.utils.type_convert import force_to_set


def test_force_to_set():
    assert force_to_set({1, 2, 3}) == {1, 2, 3}
    assert force_to_set([4, 5, 6]) == {4, 5, 6}
    assert force_to_set(['seven', 'eight']) == {'seven', 'eight'}
    assert force_to_set('nine') == {'nine'}
    assert force_to_set(100) == {100}

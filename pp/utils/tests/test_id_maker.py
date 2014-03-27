# -*- coding: utf-8 -*-
# src/pp-utils/pp/utils/tests/test_id_maker.py

##from datetime import datetime
import uuid

##from dateutil.parser import parse as dt
import pytest
from pytest import mark

import pp.utils.id_maker as idm


def test_base_id():
    # Check that the callable is callable
    assert idm.ID()() == 99


@mark.parametrize('uuid_str, slug', [
    ('aab4aa8d-0624-47c6-aa61-22d09ee426cc', 'qrSqjQYkR8aqYSLQnuQmzA'),
    ('158b7e0c-3826-4827-a2ab-8314a14b9d0e', 'FYt-DDgmSCeiq4MUoUudDg'),
    ('56a4f614-fb4b-4e80-909c-797f969adf9b', 'VqT2FPtLToCQnHl_lprfmw'),
    ('904ff1c0-7108-485f-8339-19d8bd2e843e', 'kE_xwHEISF-DORnYvS6EPg'),
])
def test_uuid_string_to_base_64_string(uuid_str, slug):
    assert idm.uuid2slug(uuid_str) == slug


def test_base_64_string_to_uuid_string():
    s2 = 'NmYDAlxwRjeQh1FXo4y5NA'
    u2 = idm.slug2uuid(s2)
    assert u2 == '36660302-5c70-4637-9087-5157a38cb934'


def test_uuid_to_string_base_64_and_back():
    random_uuid = uuid.uuid4()
    s3 = idm.uuid2slug(str(random_uuid))
    u3 = idm.slug2uuid(s3)
    random_uuid_copy = uuid.UUID(u3)
    assert random_uuid == random_uuid_copy


def test_uuid_base64():
    slug4 = idm.uuid_base64()
    u4 = idm.slug2uuid(slug4)
    # Check that equivalent UUID is valid by converting string
    valid_uuid = uuid.UUID(u4)


def test_get_id_by_name():
    pass


def test_get_sequential_id():
    pass

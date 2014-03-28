# -*- coding: utf-8 -*-
# src/pp-utils/pp/utils/tests/test_id_maker.py

##from datetime import datetime
import uuid

##from dateutil.parser import parse as dt
import pytest
from pytest import mark

import pp.utils.id_maker as idm


@mark.parametrize('long_name, short_name_length, expected_abbrev', [
    ("Vodafone", 6, "vodafn"),
    ("Vodafone", 4, "voda"),
    ("Vodafone", 10, "vodafnxxxx"),
    ("Vodafone", 1, "v"),
])
def test_hihat_with_default_stop_words_and_abbrs(long_name,
                                                 short_name_length,
                                                 expected_abbrev):
    assert idm.hihat(long_name, short_name_length) == expected_abbrev


def test_hihat_with_stop_words():
    stop_words = [
        "company",
        "corporation",
      #  "inc",
        "incorporated",
        "international",
        "limited",
      #  "ltd",
    ]
    assert idm.hihat("Lloyds Bank Ltd", 4,
                     stop_words=None) == 'lloy'
    assert idm.hihat("Lloyds Bank Ltd", 4,
                     stop_words=stop_words) == 'lblx'


@mark.parametrize('abbrevs, long_name, expected_abbrev', [
    (False, "Microsoft", "msft"),
    (True, "Microsoft", "micr"),
    (False, "Cisco", "cisc"),
    (True, "Cisco", "csco"),
])
def test_hihat_with_known_abbrevs(abbrevs, long_name, expected_abbrev):
    known_abbrevs = dict(
        exxon="xon",
        cisco="csco",
        jpmorgan="jpm",
    )
    if abbrevs:
        assert idm.hihat(long_name, 4,
                         known_abbreviations=known_abbrevs
                         ) == expected_abbrev
    else:
        assert idm.hihat(long_name, 4) == expected_abbrev


@mark.parametrize('uuid_str, slug', [
    ('aab4aa8d-0624-47c6-aa61-22d09ee426cc', 'qrSqjQYkR8aqYSLQnuQmzA'),
    ('158b7e0c-3826-4827-a2ab-8314a14b9d0e', 'FYt$DDgmSCeiq4MUoUudDg'),
    ('56a4f614-fb4b-4e80-909c-797f969adf9b', 'VqT2FPtLToCQnHl_lprfmw'),
    ('904ff1c0-7108-485f-8339-19d8bd2e843e', 'kE_xwHEISF$DORnYvS6EPg'),
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


@pytest.fixture(scope='module')
def id_gen_sec():
    return idm.id_generator('pp-sec', start_at=10001)


@pytest.fixture(scope='module')
def id_gen_usr():
    return idm.id_generator('pp-usr', start_at=101)


@mark.parametrize('arg1, start_of_id', [
    (0, 'pp-usr-000101-'),
    (5001, 'pp-usr-005001-'),
    (0, 'pp-usr-005002-'),
    ("John Smith", 'pp-usr-johnsm'),
    (0, 'pp-usr-005003-'),
])
def test_get_user_ids(arg1, start_of_id, id_gen_usr):
    user_id = id_gen_usr(arg1)
    assert user_id.startswith(start_of_id)
    assert len(user_id) == 36


@mark.parametrize('arg1, start_of_id', [
    (6001, 'pp-sec-006001-'),
    (0, 'pp-sec-006002-'),
    ("Lloyds Bank", 'pp-sec-lloyds'),
    (0, 'pp-sec-006003-'),
])
def test_get_security_ids(arg1, start_of_id, id_gen_sec):
    sec_id = id_gen_sec(arg1)
    assert sec_id.startswith(start_of_id)
    assert len(sec_id) == 36


def test_get_sequential_id():
    pass

if __name__ == '__main__':
    print("Starting...\n")

    id_gen_usr = idm.id_generator('pp-usr', start_at=101)
    print(id_gen_usr(0))
    print(id_gen_usr(5001))
    print(id_gen_usr(0))

##    test_get_user_ids(0, 'pp-usr-000101-')
    print("\nFinished.")
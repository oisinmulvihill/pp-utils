# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.parser import parse as dt
from pprint import pprint

import pytest

from pp.utils.options import OptionsList, OptionLineError


def _get_text(lines):
    """Join text lines and add trailing c/r"""
    return "\n".join(lines) + "\n"


def test_comments_and_blank_lines_preserved():
    lines = [
        "# This is a comment",
        "     # This comment is indented, but will be moved to left",
        "availability : am | eve | pm",
        "          ",  # Intentionally blank
        "# A final comment",
    ]
    text = _get_text(lines)
    opt_list = OptionsList(text)
    assert opt_list.lines[0] == "# This is a comment"
    assert opt_list.lines[1].startswith("# This comment")
    assert opt_list.lines[3] == ""


def test_cant_start_text_with_continuation():
    text = "| more-options"
    with pytest.raises(OptionLineError) as exc:
        opt_list = OptionsList(text)
    assert "You can't start" in exc.value.message


def test_parse_line():
    line = "availability : am | eve | pm"
    opt_list = OptionsList()
    key, options = opt_list._parse_line(line)
    assert key == 'availability'
    assert options == set(['am', 'eve', 'pm'])


def test_parse_line_with_no_colon_or_bar():
    line = "Just a line of text"
    opt_list = OptionsList()
    with pytest.raises(OptionLineError) as exc:
        opt_list._parse_line(line)
    assert "needed in line" in exc.value.message


def test_parse_text_1():
    text = "availability : am | eve | pm"
    opt_list = OptionsList(text)
    opt_list.options['availability'] == set(['am', 'eve', 'pm'])


def test_parse_text_2():
    text = """\
availability : am | eve | pm
importance   : b | c | a
# Note: intentional duplication removed from output
internet     : offline | connected | offline
"""
    opt_list = OptionsList(text)
    assert opt_list.options['availability'] == set(['am', 'eve', 'pm'])
    assert opt_list.options['importance'] == set(['a', 'b', 'c'])
    assert opt_list.options['internet'] == set(['connected', 'offline'])
    assert opt_list.lines[1].endswith("a | b | c")
    assert opt_list.text == """\
availability : am | eve | pm
importance   : a | b | c
# Note: intentional duplication removed from output
internet     : connected | offline
"""

def test_blank_options_ignored():
    text = "importance:a| b || d"
    opt_list = OptionsList(text)
    assert opt_list.text == "importance : a | b | d\n"


@pytest.mark.parametrize("text_line, key", [
    (": d | e | f", ""),
    ("time value : 1 | 2 | 3", "time value"),
])
def test_bad_keys_rejected(text_line, key):
    with pytest.raises(OptionLineError) as exc:
        opt_list = OptionsList(text_line)
    assert exc.value.message.startswith('Bad key "{}"'.format(key))


def test_missing_colon_rejected():
    text = "foo d | e | f"
    with pytest.raises(OptionLineError) as exc:
        opt_list = OptionsList(text)
    assert exc.value.message.startswith('One ":" needed in line')


def test_duplicate_options_across_keys_rejected():
    text = """\
availability : am | eve | pm
importance   : b | c | a
names        : adam | eve | bill
"""
    with pytest.raises(OptionLineError) as exc:
        opt_list = OptionsList(text)
    assert exc.value.message.startswith("Duplicate options")


def test_options_set_in_parse_text():
    text = """\
status      : queued | started | nearly-done | finished | on-hold
supermarket : morrisons | sainsburys | tesco
"""
    opt_list = OptionsList("# This will be overwritten")
    opt_list.parse_text(text)
    assert 'started' in opt_list.options['status']
    assert len(opt_list.options['status']) == 5
    assert len(opt_list.rev_options) == 8


def test_handles_continuation_lines():
    text = """\
location : banbury | isleworth | kings-sutton | south-bank-centre
           | whitnash
"""
    opt_list = OptionsList(text)
    assert len(opt_list.options['location']) == 5
    assert opt_list.rev_options['whitnash'] == 'location'

@pytest.mark.parametrize("source, max_line_length, expected", [
    ("a | b | c", 20, ["a | b | c"]),
    ("a | b | c | d | e", 5, ["a | b | c | d | e"]),
    ("a | b | c | d | e", 4, ["a | b | c | d", "| e"]),
    ("a | b | c | d | e", 2, ["a | b", "| c | d", "| e"]),
    ("a | b | c", 1, ["a", "| b", "| c"]),
])
def test_split_options(source, max_line_length, expected):
    opt_list = OptionsList()
    sopts = opt_list._split_options
    assert sopts(source, max_line_length) == expected


def test_init_with_long_lines():
    text = """\
location : banbury | isleworth | kings-sutton | south-bank-centre
           | whitnash
"""
    opt_list1 = OptionsList(text, 70)
    assert opt_list1.text == "location : banbury | isleworth | " + \
           "kings-sutton | south-bank-centre | whitnash\n"
    opt_list2 = OptionsList(text)  # Default max_line_length = 60
    assert opt_list2.text == """\
location : banbury | isleworth | kings-sutton | south-bank-centre
           | whitnash
"""
    opt_list3 = OptionsList(text, 45)
    assert opt_list3.text == """\
location : banbury | isleworth | kings-sutton
           | south-bank-centre | whitnash
"""
    opt_list4 = OptionsList(text, 30)
    assert opt_list4.text == """\
location : banbury | isleworth
           | kings-sutton
           | south-bank-centre
           | whitnash
"""

def test_full_text_input():
    text = """\
# environment.txt
# For ease of reading and editing, using options format.

availability : pm |am | eve | pm
importance   : a | c| b
internet     : connected | offline
location     : banbury | isleworth | kings-sutton | south-bank-centre
               | whitnash | bognor-regis | glasgow | worthing | lands-end
               ||| shopping-in-leamingtion || deddington
# Status uses words rather than dates now
status       : queued | started | nearly-done | finished | on-hold
supermarket  : morrisons | sainsburys | tesco | asda | m&s
urgency      : sometime | this-month | this-week | today | tomorrow
weather      : fine | rain | showers
"""
    opt_list5 = OptionsList(text, 60)
    print("*" * 40)
    print(opt_list5.text)
    assert opt_list5.text == """\
# environment.txt
# For ease of reading and editing, using options format.

availability : am | eve | pm
importance   : a | b | c
internet     : connected | offline
location     : banbury | bognor-regis | deddington | glasgow | isleworth
               | kings-sutton | lands-end | shopping-in-leamingtion
               | south-bank-centre | whitnash | worthing
# Status uses words rather than dates now
status       : finished | nearly-done | on-hold | queued | started
supermarket  : asda | m&s | morrisons | sainsburys | tesco
urgency      : sometime | this-month | this-week | today | tomorrow
weather      : fine | rain | showers
"""

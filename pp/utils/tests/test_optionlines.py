# -*- coding: utf-8 -*-
# test_optionlines.py

from datetime import datetime
from dateutil.parser import parse as dt
from pprint import pprint

import pytest

from pp.utils.optionlines import (CommentLine, OptionLine, OrdinaryLine,
                                  TaskLine, BlankLine,
                                  OptionLines,
                                  OptionLineFactory,
                                  OptionLineError, OptionSubsetError)


@pytest.mark.parametrize("source_line, indent, text, is_valid_comment", [
    ("# This is a comment", 0, "# This is a comment", True),
    ("    # Comment", 4, "# Comment", True),
    ("\t\t \t\t # Comment 2", 6, "# Comment 2", True),
    ("    Missing the hash", 4, "Missing the hash", False),
])
def test_comments(source_line, indent, text, is_valid_comment):
    comment_line = CommentLine(source_line)
    assert comment_line.indent == indent
    assert comment_line.text == text
    assert comment_line.validates() == is_valid_comment


def test_valid_option_line():
    source_line = "importance :: a | b | c"
    option_line = OptionLine(source_line)
    assert option_line.indent == 0
    assert option_line.key == 'importance'
    assert option_line.options == set(["a", "b", "c"])
    assert option_line.validates()
    assert option_line.text == source_line


def test_empty_option_items_ignored():
    source_line = "urgency::1| 2 || 3"
    option_line = OptionLine(source_line)
    assert option_line.key == 'urgency'
    assert option_line.options == set(["1", "2", "3"])
    assert option_line.validates()
    assert option_line.text == "urgency :: 1 | 2 | 3"


def test_no_options_ok_to_declare_key():
    source_line = "some_input_any_value_ok ::"
    option_line = OptionLine(source_line)
    assert option_line.key == 'some_input_any_value_ok'
    assert option_line.options == set()
    assert option_line.validates()


def test_multiple_double_colons_accepted():
    source_line = "bar:: a | bbb:27| c::95| d||"
    option_line = OptionLine(source_line)
    assert option_line.key == 'bar'
    assert option_line.options == set(["a", "bbb:27", "c::95", "d"])
    assert option_line.text == "bar :: a | bbb:27 | c::95 | d"


@pytest.mark.parametrize("source_line, is_task_line", [
    ("  [ ] Fix the bathroom door", True),
    ("* [>] Apply for deed of variation", True),
    ("* [x] Contact agency re contract", True),
    ("! [-] No such emphasis char", False),
    ("**[@] No such status char", False),
    ("[]", False),  # Task text missing
    ("][", False),
    ("[Badly formatted task]", False),
    ("No brackets", False),
    ("[ Only one left bracket", False),
    ("] Only one right bracket", False),
    ("* [ ] Two status chars possible?", True),
])
def test_task_line(source_line, is_task_line):
    # print(source_line)
    task_line = TaskLine(source_line)
    assert task_line.validates() == is_task_line
    if is_task_line:
        assert task_line.text == source_line.strip()


@pytest.mark.parametrize("source_line, status_ch, status, emph_ch, emph", [
    ("* [x] Contact agency re contract", "x", "finished", "*", "urgent"),
    ("  [>] Do this later", ">", "later", "", "not-urgent"),
    ("[-] Cancelled this one", "-", "cancelled", "", "not-urgent"),
    ("**[ ] Desperate measures", "", "to-do", "**", "today"),
])
def test_task_line_status_text(source_line, status_ch, status, emph_ch, emph):
    task_line = TaskLine(source_line)
    assert task_line.status_ch == status_ch
    assert task_line.status == status
    assert task_line.emphasis_ch == emph_ch
    assert task_line.emphasis == emph
    # assert task_line.task_text == "Contact agency re contract"
    assert task_line.text == source_line.strip()


def test_not_an_option_line():
    source_line = "  Just an ordinary piece of text"
    option_line = OptionLine(source_line)
    assert option_line.indent == 2
    assert option_line.key is None
    assert not option_line.validates()


@pytest.mark.parametrize("source_line, key", [
    (":: d | e | f", ""),
    ("time value :: 1 | 2 | 3", "time value"),
])
def test_invalid_option_line_with_bad_keys_rejected(source_line, key):
    with pytest.raises(OptionLineError) as exc:
        option_line = OptionLine(source_line)
    assert exc.value.message.startswith('Bad key "{}"'.format(key))


@pytest.mark.parametrize("source_line, class_name", [
    ("# Starting with a comment", 'CommentLine'),
    ("importance :: a | b | c", 'OptionLine'),
    ("Mary had a little lamb", 'OrdinaryLine'),
    ("", 'BlankLine'),
    ("                ", 'BlankLine'),
    ("\n", 'BlankLine'),
])
def test_option_line_factory_individual_lines(source_line, class_name):
    factory = OptionLineFactory()
    lines = []
    line_obj = factory.make_line(source_line)
    assert line_obj.__class__.__name__ == class_name


def test_option_line_factory_from_text_block():
    source_text = """\
# Starting with a comment
importance :: a | b | c
Mary had a little lamb
    [x] This task has been finished


asdasd asdasd
"""
    factory = OptionLineFactory()
    class_names = []
    print(source_text.splitlines())
    for source_line in source_text.rstrip().splitlines():
        line_obj = factory.make_line(source_line)
        class_names.append(line_obj.__class__.__name__)
    assert class_names == ['CommentLine', 'OptionLine', 'OrdinaryLine',
                           'TaskLine',
                           'BlankLine', 'BlankLine', 'OrdinaryLine']


def test_option_lines_from_text_block():
    source_text = """\
# This is a comment
    importance :: a | b | c
Mary had a little lamb
    [x] This task has been finished


defdef defdef
"""
    option_lines = OptionLines(source_text)
    # print(option_lines)
    assert str(option_lines) == source_text.rstrip()
    assert option_lines.lines[0] == "# This is a comment"
    assert option_lines.lines[1].startswith("    imp")
    assert len(option_lines.lines) == 7
    # assert 0,3


def test_duplicate_option_keys_rejected():
    source_text = """\
names :: x | y | z
foo   :: 1 | 2 | 3
names :: adam | bill | charlie
"""
    with pytest.raises(OptionLineError) as exc:
        option_lines = OptionLines(source_text)
    assert exc.value.message.startswith("Duplicate option keys")


def test_duplicate_options_across_keys_rejected():
    source_text = """\
availability :: am | eve | pm
importance   :: b | c | a
names        :: adam | eve | bill
"""
    with pytest.raises(OptionLineError) as exc:
        option_lines = OptionLines(source_text)
    assert exc.value.message.startswith("Duplicate options")


def test_options_set_in_parse_text():
    source_text = """\
status      :: queued | started | nearly-done | finished | on-hold
supermarket :: morrisons | sainsburys | tesco
"""
    option_lines = OptionLines("# This will be overwritten")
    option_lines.parse_text(source_text)
    assert 'started' in option_lines.all_keys['status'].options
    assert len(option_lines.all_keys['status'].options) == 5
    assert len(option_lines.all_options) == 8


def test_parse_text_2():
    source_text = """\
availability :: am | eve | pm
importance   :: b | c | a
# Note: intentional duplication removed from output
internet     :: offline | connected | offline
"""
    option_lines = OptionLines(source_text)
    assert option_lines.all_keys['availability'
                                 ].options == set(['am', 'eve', 'pm'])
    assert option_lines.all_keys['importance'
                                 ].options == set(['a', 'b', 'c'])
    assert option_lines.all_keys['internet'
                                 ].options == set(['connected', 'offline'])
    assert option_lines.lines[1] == "importance   :: a | b | c"
    assert str(option_lines) == """\
availability :: am | eve | pm
importance   :: a | b | c
# Note: intentional duplication removed from output
internet     :: connected | offline"""


def test_full_text_input_3():
    source_text = """\
# environment.txt
# For ease of reading and editing, using options format.

availability :: pm |am | eve | pm
importance   :: a | c| b
internet     :: connected | offline
location     :: banbury | isleworth | kings-sutton | south-bank-centre
                | whitnash | bognor-regis | glasgow | worthing
                | lands-end||| shopping-in-leamington || deddington
# Status uses words rather than dates now
status       :: queued | started | nearly-done | finished | on-hold
supermarket  :: morrisons | sainsburys | tesco | asda | m&s
urgency      :: sometime | this-month | this-week | today | tomorrow
weather      :: fine | rain | showers
"""
    # opt_list5 = OptionsList(text, 65)
    option_lines = OptionLines(source_text)
    assert len(option_lines) == 12
    # print("*" * 40)
    # print(option_lines)
    assert str(option_lines) == """\
# environment.txt
# For ease of reading and editing, using options format.

availability :: am | eve | pm
importance   :: a | b | c
internet     :: connected | offline
location     :: banbury | bognor-regis | deddington | glasgow
                | isleworth | kings-sutton | lands-end
                | shopping-in-leamington | south-bank-centre
                | whitnash | worthing
# Status uses words rather than dates now
status       :: finished | nearly-done | on-hold | queued | started
supermarket  :: asda | m&s | morrisons | sainsburys | tesco
urgency      :: sometime | this-month | this-week | today | tomorrow
weather      :: fine | rain | showers"""


def test_option_lines_check_is_subset_of():
    outer_text = """\
# environment, listing all possibilities.
availability :: am | eve | pm
internet     :: connected | offline
weather      :: fine | rain | showers"""
    inner_text = """\
internet     :: connected
weather      :: rain | showers"""
    opt_lines_outer = OptionLines(outer_text)
    opt_lines_inner = OptionLines(inner_text)
    # Raises exception if not subset
    opt_lines_inner.check_is_subset_of(opt_lines_outer)


def test_option_lines_check_is_subset_of_bad_option():
    outer_text = "weather :: fine | rain | showers"
    inner_text = "weather :: cloudy"
    opt_lines_outer = OptionLines(outer_text)
    opt_lines_inner = OptionLines(inner_text)
    with pytest.raises(OptionSubsetError) as exc:
        opt_lines_inner.check_is_subset_of(opt_lines_outer)
    assert exc.value.message.startswith(
        "['cloudy'] not found in \"weather\" options")


def test_option_lines_check_is_subset_of_bad_key():
    outer_text = "weather :: fine | rain | showers"
    inner_text = "foo :: bar"
    opt_lines_outer = OptionLines(outer_text)
    opt_lines_inner = OptionLines(inner_text)
    with pytest.raises(OptionSubsetError) as exc:
        opt_lines_inner.check_is_subset_of(opt_lines_outer)
    assert exc.value.message.startswith('"foo" not found as option key')


@pytest.mark.parametrize("source_line, max_option_length, expected", [
    ("a | b | c", 20, ["a | b | c"]),
    ("a | b | c | d | e", 17, ["a | b | c | d | e"]),
    ("a | b | c | d | e", 13, ["a | b | c | d", "| e"]),
    ("a | b | c | d | e", 7, ["a | b", "| c | d", "| e"]),
    ("a | b | c", 3, ["a", "| b", "| c"]),
    ("banbury | isleworth | kings-sutton | south-bank-centre", 58,
        ["banbury | isleworth | kings-sutton | south-bank-centre"]),
])
def test_wrap_options(source_line, max_option_length, expected):
    opt_line = OptionLine()
    opts_gen = (opt.strip() for opt in source_line.split('|'))
    opt_line.options = set(opt for opt in opts_gen if len(opt))
    # print(source_line, max_option_length)
    # print(opt_line.options)
    assert opt_line._wrap_options(max_option_length) == expected


def test_handles_continuation_lines():
    source_text = """\
location :: banbury | isleworth | kings-sutton | south-bank-centre
            | whitnash
"""
    opt_lines = OptionLines(source_text)
    assert len(opt_lines) == 1
    assert len(opt_lines.all_keys['location'].options) == 5
    assert opt_lines.all_options['whitnash'].key == 'location'
    assert str(opt_lines) == """\
location :: banbury | isleworth | kings-sutton | south-bank-centre
            | whitnash"""


def test_continuation_lines_2a333():
    source_text = """\
location1234 :: banbury | isleworth | kings-sutton | south-bank-centre
                | whitnash | bognor-regis | glasgow | worthing
                | lands-end||| shopping-in-leamington || deddington
"""
    expected = """\
location1234 :: banbury | bognor-regis | deddington | glasgow
                | isleworth | kings-sutton | lands-end
                | shopping-in-leamington | south-bank-centre
                | whitnash | worthing"""
    opt_lines = OptionLines(source_text)
    assert str(opt_lines) == expected


def test_cant_start_text_with_continuation():
    return #xxxxxxxxxxxxxxx
    source_text = "| more-options"
    with pytest.raises(OptionLineError) as exc:
        opt_lines = OptionLines(source_text)
    assert "You can't start" in exc.value.message

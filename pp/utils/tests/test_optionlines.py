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
                                  OptionLineError)


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


def test_empty_options_ignored():
    source_line = "urgency::1| 2 || 3"
    option_line = OptionLine(source_line)
    assert option_line.key == 'urgency'
    assert option_line.options == set(["1", "2", "3"])
    assert option_line.validates()


def test_multiple_double_colons_accepted():
    source_line = "bar:: a | bbb:27| c::95| d||"
    option_line = OptionLine(source_line)
    assert option_line.key == 'bar'
    assert option_line.options == set(["a", "bbb:27", "c::95", "d"])


@pytest.mark.parametrize("source_line, is_task_line", [
    ("  [ ] Fix the bathroom door", True),
    ("* [>] Apply for deed of variation", True),
    ("* [x] Contact agency re contract", True),
    ("+ [-] No such emphasis char", False),
    ("[]", False),  # Task text missing
    ("][", False),
    ("[Badly formatted task]", False),
    ("No brackets", False),
    ("[ Only one left bracket", False),
    ("] Only one right bracket", False),
    ("* [  ] Two status chars possible", True),
])
def test_task_line(source_line, is_task_line):
    # print(source_line)
    task_line = TaskLine(source_line)
    assert task_line.validates() == is_task_line


def test_task_line_status_text():
    source_line = "* [x] Contact agency re contract"
    task_line = TaskLine(source_line)
    assert task_line.status_ch == "x"
    assert task_line.status == "finished"
    assert task_line.emphasis_ch == "*"
    assert task_line.emphasis
    assert task_line.task_text == "Contact agency re contract"


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


defdef defdef
"""
    option_lines = OptionLines(source_text)
    # print(option_lines)
    assert str(option_lines) == source_text.rstrip()
    assert option_lines.lines[0] == "# This is a comment"
    assert option_lines.lines[1].startswith("    imp")
    assert len(option_lines.lines) == 6
    # assert 0,3
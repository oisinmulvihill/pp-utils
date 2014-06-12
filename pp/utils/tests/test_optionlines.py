# -*- coding: utf-8 -*-
# test_optionlines.py

from datetime import datetime
from dateutil.parser import parse as dt
from pprint import pprint

import pytest

from pp.utils.optionlines import (CommentLine, OptionLine, OrdinaryLine,
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
    assert option_line.validates()


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
    assert obj.__class__.__name__ == class_name


def test_option_line_factory_from_text_block():
    source_text = """\
# Starting with a comment
importance :: a | b | c
Mary had a little lamb

\n
"""
    factory = OptionLineFactory()
    class_names = []
    for source_line in source_text.splitlines():
        line_obj = factory.make_line(source_line)
        class_names.append(line_obj.__class__.__name__)
    assert class_names == ['CommentLine', 'OptionLine', 'OrdinaryLine',
                           'BlankLine', 'BlankLine', 'BlankLine']

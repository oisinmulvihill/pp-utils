# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.parser import parse as dt
from pprint import pprint

import pytest

from pp.utils.options import OptionsList, OptionLineError


def _get_text(lines):
    """Join text lines and add trailing c/r"""
    return "\n".join(lines) + "\n"


def test_load_options():
    assert 0 == 0



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
    opt_list = OptionsList("")
    key, options = opt_list._parse_line(line)
    assert key == 'availability'
    assert options == set(['am', 'eve', 'pm'])


def test_parse_line_with_no_colon_or_bar():
    line = "Just a line of text"
    opt_list = OptionsList("")
    with pytest.raises(OptionLineError) as exc:
        opt_list._parse_line(line)
    assert "needed in line" in exc.value.message


def test_parse_lines_1():
    text = "availability : am | eve | pm"
    opt_list = OptionsList(text)
    opt_list.keys['availability'] == set(['am', 'eve', 'pm'])


def test_parse_lines_2():
    text = """\
availability : am | eve | pm
importance   : b | c | a
# Note: intentional duplication removed from output
internet     : offline | connected | offline
"""
    opt_list = OptionsList(text)
    assert opt_list.keys['availability'] == set(['am', 'eve', 'pm'])
    assert opt_list.keys['importance'] == set(['a', 'b', 'c'])
    assert opt_list.keys['internet'] == set(['connected', 'offline'])
    assert opt_list.lines[1].endswith("a | b | c")
    assert opt_list.text == """\
availability : am | eve | pm
importance   : a | b | c
# Note: intentional duplication removed from output
internet     : connected | offline
"""

def test_duplicate_options_rejected():
    text = """\
availability : am | eve | pm
importance   : b | c | a
names        : adam | eve | bill
"""
    with pytest.raises(OptionLineError) as exc:
        opt_list = OptionsList(text)
    exc.value.message.startswith("Duplicate options")

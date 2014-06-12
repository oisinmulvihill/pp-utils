# -*- coding: utf-8 -*-
# pp/utils/optionlines.py

"""
Options format is designed to make reading/writing data simple.
OptionLines features:
    Key to options separated by "::" to avoid confusion with ":" in text.
    Options separated by vertical bar.
    Vertical bar starts continuation line
    Options in each lines sorted
OptionList features:
    Options should be unique between keys, not just within one key.
    Line order and blank lines preserved
    Comments preserved


Example data for TaskNav environment file:

    # environment.txt
    # For ease of reading and editing, using options format.

    availability :: am | eve | pm
    importance   :: a | b | c
    internet     :: connected | offline
    location     :: banbury | isleworth | kings-sutton | south-bank-centre
                    | whitnash
    # Status uses words rather than dates now
    status       :: queued | started | nearly-done | finished | on-hold
    supermarket  :: morrisons | sainsburys | tesco
    urgency      :: sometime | this-month | this-week | today | tomorrow
    weather      :: fine | rain | showers


Different types of line to think about
======================================
option
  importance :: a | b | c
comment
  # This is a comment
caption
  [ ] Buy strawberry yoghurt
note
  Special offer on Thursday
subtask
  [ ] Research yoghurt prices
statuses
  [ ] to-do
  [/] started
  [x] finished
  [-] cancelled
  [>] moved
timeline
  date-created
  date-started
  date-finished
"""

from abc import abstractmethod


KEY_OPTIONS_SEPARATOR = '::'


class OptionLineError(Exception):
    pass


class BaseOptionLine(object):
    """One line of an OptionList, printed with double colon and bars
    as separators, e.g.
       availability :: am | eve | pm
    Each line should be independent of the others, apart from the options
    continuation scheme, which has worked well.
    """

    def __init__(self, source_line=""):
        self.source_line = source_line.rstrip()
        self.text = self.source_line.lstrip()
        self.indent = len(self.source_line) - len(self.text)
        # self.parse_text(source_text)

    @abstractmethod
    def validates(self):
        pass

    # @abstractmethod
    # def parse_text(self, source_text):
    #     pass


class CommentLine(BaseOptionLine):
    """Any line whose first non-white-space char is '#'
    """

    def validates(self):
        """True if the source_line is a comment"""
        return self.text.startswith("#")


class OptionLine(BaseOptionLine):
    """A line that has a key, then the double colon, with 0 to many options
    """

    def __init__(self, source_line=""):
        super(OptionLine, self).__init__(source_line)
        try:
            split_text = self.text.split(KEY_OPTIONS_SEPARATOR, 1)
            self.key, opts = [x.strip() for x in split_text]
            # This is an OptionLine: check that key is a single word
            if len(self.key.split()) != 1:
                msg = 'Bad key "{}" in line "{}"'
                raise OptionLineError(msg.format(self.key, self.text))
        except ValueError:
            # KEY_OPTIONS_SEPARATOR was missing, so not an OptionLine
            self.key = None

    def validates(self):
        """This is an OptionLine if we have successfully parsed a key"""
        return bool(self.key)


class BlankLine(BaseOptionLine):

    def validates(self):
        return not len(self.text) and not self.indent


class OrdinaryLine(BaseOptionLine):

    def validates(self):
        return len(self.text) > 0


class OptionLineFactory(object):
    """Creates the right type of option line.
    """
    line_classes = [
        # List of lines, in decreasing strictness order
        CommentLine,
        BlankLine,
        OptionLine,
        OrdinaryLine,
    ]

    def make_line(self, source_line):
        for class_ in self.line_classes:
            line_obj = class_(source_line)
            if line_obj.validates():
                return line_obj
        else:
            msg = 'Unknown line type for option line "{}"'
            raise OptionLineError(msg.format(source_line))


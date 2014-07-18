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
status
  [ ] to-do
  [/] started
  [x] finished
  [-] cancelled
  [>] moved (or postponed)
emphasis
  *  True
timeline
  date-created
  date-started
  date-finished

TO-DO after all working:
[x] Duplicate keys across lines rejected
[x] duplicate_options_across_keys_rejected
[x] Options subset
[x] Continuation lines
[x] Alignment of double colons
[/] Subset return T/F or Exception?
[x] OptionLine key and options forced to lower case
[ ] Task continuation lines
[ ] Put tasks together, and options together?
[ ] When changing the order:
    [ ] Comments to stay with following line
    [ ] Blanks to stay with following line
Next steps
==========
[ ] Sort out the indents in the output
"""

import sys
from abc import abstractmethod
from pprint import pprint

COMMENT_CHAR = '#'
KEY_OPTIONS_SEPARATOR = '::'
MAX_OPTION_LINE_LENGTH = 70
OPT_CONTIN_CHAR = '|'
TASK_STATUS_DICT = {
    "": "to-do",
    "/": "started",
    "x": "finished",
    "-": "cancelled",
    ">": "later",
}
TASK_EMPHASIS_DICT = {
    "": "non-urgent",
    "*": "urgent",
    "**": "today",
}


class OptionLineError(Exception):
    pass


class OptionSubsetError(Exception):
    pass


class BaseOptionLine(object):
    """One line of an OptionList, printed with double colon and bars
    as separators, e.g.
       availability :: am | eve | pm
    Each line should be independent of the others, apart from the options
    continuation scheme, which has worked well.
    self.lines_container is for use when a member of an OptionLines list.
    """

    def __init__(self, source_line=""):
        self.source_line = source_line.rstrip()
        self._text = self.source_line.lstrip()
        self.indent = len(self.source_line) - len(self._text)
        self.preceding_lines = []  # e.g. Comment lines
        self.continuation_line_objs = []  # e.g. for options and tasks
        self.lines_container = None
        self._parse_line()

    @property
    def text(self):
        """Return the text string that follows any white space indent"""
        return self._format_line()

    @abstractmethod
    def validates(self):
        """This is called after _parse_line(), if defined.
        Return True if source_line is the given line type."""

    def _format_line(self):
        return self._text

    def _parse_line(self):
        pass


class BlankLine(BaseOptionLine):

    def validates(self):
        return not len(self._text) and not self.indent


class CommentLine(BaseOptionLine):
    """Any line whose first non-white-space char is '#'
    """

    def validates(self):
        """True if the source_line is a comment"""
        return self._text.startswith(COMMENT_CHAR)


class ContinuationLine(BaseOptionLine):
    """Line to be attached to previous non-continuation line"""


class OptionContinuationLine(ContinuationLine):
    """Any line whose first non-white-space char is '|'
    """

    def validates(self):
        return self._text.startswith(OPT_CONTIN_CHAR)


class OptionLine(BaseOptionLine):
    """A line that has a key, then the double colon, with 0 to many options
    """

    # def __init__(self, source_line=""):
    #     super(OptionLine, self).__init__(source_line)
    #     # self.max_key_length = 0  # Increases width of first column, if > 0
    option_join_str = " {} ".format(OPT_CONTIN_CHAR)

    def __init__(self, source_line=""):
        self.key = None
        self.options = None
        super(OptionLine, self).__init__(source_line)

    def validates(self):
        """This is an OptionLine if we have successfully parsed a key"""
        return bool(self.key)

    def _format_line(self):
        """Return canonical text form of option line. This may be split
        into multiple lines, if line would exceed max_line_length.
        """
        options_str = self.option_join_str.join(sorted(self.options))
        # NB String format can have arg {0} here as "" but not 0
        try:
            max_key_len = self.lines_container.max_key_length or ""
        except AttributeError:
            max_key_len = len(self.key)
        if self.lines_container:
            max_option_len = self.lines_container.max_option_length
        else:
            max_option_len = sys.maxsize  # Python 3==> not sys.maxint
        continuation_line_objs = []
        split_option_lines = self._wrap_options(max_option_len)
        first_prefix = "{1:{0}} {2} ".format(max_key_len, self.key,
                                             KEY_OPTIONS_SEPARATOR)
        continuation_prefix = "{1:{0}} {2} ".format(
            max_key_len, "", " " * len(KEY_OPTIONS_SEPARATOR))
        result_lines = [first_prefix + split_option_lines[0]]
        for cont_line in split_option_lines[1:]:
            result_lines.append(continuation_prefix + cont_line)
        return "\n".join(result_lines)

    def _parse_line(self):
        try:
            split_text = self._text.split(KEY_OPTIONS_SEPARATOR, 1)
            self.key, opts = [x.strip().lower() for x in split_text]
            # This is an OptionLine, so check that key is a single word
            if len(self.key.split()) != 1:
                msg = 'Bad key "{}" in line "{}"'
                raise OptionLineError(msg.format(self.key, self._text))
            opt_gen = (opt.strip() for opt in opts.split(OPT_CONTIN_CHAR))
            # Check length of opt rather than bool() to allow for opt=0
            self.options = set(opt for opt in opt_gen if len(opt))
        except ValueError:
            # KEY_OPTIONS_SEPARATOR was missing, so not an OptionLine
            self.key = None
            self.options = None

    def _wrap_options(self, max_option_length):
        """Split options into multiple strings to deal with long lists"""
        ## if not max_option_length:
        ##     max_option_length = sys.maxsize  # Python 3==> not sys.maxint
        result_lines = []
        current_line = []
        # current_length starts at -3 to allow for no leading separator
        current_length = -3

        for opt in sorted(self.options):
            if current_length + 3 + len(opt) <= max_option_length:
                current_line.append(opt)
                current_length += 3 + len(opt)
            else:
                # Need to start a new line
                result_lines.append(self.option_join_str.join(current_line))
                current_line = [OPT_CONTIN_CHAR + ' ' + opt]
                current_length = 2 + len(opt)
        if current_line:
            result_lines.append(self.option_join_str.join(current_line))
        return result_lines


class TaskContinuationLine(ContinuationLine):

    def validates(self):
        return len(self._text) > 0


class TaskLine(BaseOptionLine):
    """ Line that begins with '[' and ']' within the first 6 chars,
        to form a status box.
        Includes continuation lines
    e.g.
          [ ] Fix the bathroom door
        * [>] Apply for deed of variation
        + [x] Contact agency re contract
    """

    def validates(self):
        """Return True if the source_line, after parsing, has a task."""
        return bool(self.task_text)

    def _format_line(self):
        """Return text part of task line, after the indent"""
        emphasis_and_status = "{:2}[{:1}]".format(self.emphasis_chars,
                                                  self.status_ch)
                                                  #.strip()
        return " ".join([emphasis_and_status, self.task_text])

    def _parse_line(self):
        parts = self._text.split("]")
        try:
            emphasis, status = parts[0].strip().split("[")
            self.emphasis_chars = emphasis.strip()
            self.emphasis = TASK_EMPHASIS_DICT[self.emphasis_chars]
            self.status_ch = status.strip()
            self.status = TASK_STATUS_DICT[self.status_ch]
            self.task_text = parts[1].strip()
            # So this is a task. Decrement indent by 2 if no emphasis
            if not self.emphasis_chars:
                self.indent -= 2
            print(">>----{:15}{:3} ({}, {})".format(
                self.task_text[:15], "...", self.emphasis, self.status))
        except (ValueError, IndexError, KeyError):
            # ValueError if brackets are missing
            # IndexError if there is no parts[1], i.e. only parts[0]
            # KeyError if lookup fails on a TASK_EMPHASIS/STATUS_DICT
            self.status_text = None
            self.task_text = None


class OptionLineFactory(object):
    """Creates the right type of option line.
    """
    line_classes = [
        # List of lines, in decreasing strictness order
        CommentLine,
        BlankLine,
        TaskLine,
        OptionLine,
        OptionContinuationLine,
        TaskContinuationLine,
    ]

    def __init__(self, lines_container=None):
        self.lines_container = lines_container

    def make_line(self, source_line):
        for class_ in self.line_classes:
            line_obj = class_(source_line)
            if line_obj.validates():
                line_obj.lines_container = self.lines_container
                return line_obj
        else:
            msg = 'Unknown line type for option line "{}"'
            raise OptionLineError(msg.format(source_line))


class OptionLines(object):
    """This is a list of consecutive BaseOptionLine objects."""

    def __init__(self, source_text="",
                 max_line_length=MAX_OPTION_LINE_LENGTH):
        self.max_line_length = max_line_length
        # TO-DO Check max_option_length setting. Here is a sensible default.
        self.max_option_length = max(self.max_line_length - 20, 30)
        self._obj_lines = []  # Or use a MutableMapping instead?
        self.option_keys = {}
        self.all_options = {}
        self.tasks = []
        self.line_factory = OptionLineFactory(self)
        self.parse_text2(source_text)

    def __len__(self):
        return len(self._obj_lines)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.format_text()

    def check_is_option_subset_of(self, outer_opt_lines):
        """Return if all option keys are found in outer_opt_lines,
        and for each key, the options are in the outer_opt_lines options.
        Otherwise, raise OptionSubsetError, with error message. This was
        done (rather than just return T/F) to give the user some indication
        of what has gone wrong.
        """
        # for key, inner_options in self.options.iteritems():
        for key in self.option_keys:
            inner_options = self.option_keys[key].options
            try:
                outer_options = outer_opt_lines.option_keys[key].options
                if not inner_options.issubset(outer_options):
                    unknowns = inner_options.difference(outer_options)
                    msg = '{} not found in "{}" options: {}'.format(
                        sorted(unknowns), key, sorted(outer_options))
                    raise OptionSubsetError(msg)
            except KeyError:
                msg = '"{}" not found as option key in {}'.format(
                      key, outer_opt_lines.option_keys.keys())
                raise OptionSubsetError(msg)

    def format_text(self, max_line_length=None):
        """Return lines in canonical output form. This is a public
        function, to allow for various output max_line_lengths.
        Recalculate the maximum option key length, in case something has
        changed since the lines were parsed.
        """
        if max_line_length is None:
            max_line_length = self.max_line_length
        self._calc_maximum_key_length()  # into self.max_key_length
        # Allow 4 chars for " :: " in between key and options
        self.max_option_length = max_line_length - self.max_key_length - 4

        output_lines = []
        # output_lines.append(">>>>>")
        for line_obj in self._obj_lines:
            output_lines.append(" " * line_obj.indent + line_obj.text)
        # output_lines.append("<<<<<")
        return "\n".join(output_lines)

    @property
    def lines(self):
        return self.format_text().splitlines()

    def parse_text2(self, source_text):
        '''
        Need to have state transition diagram here
        OptionLine
        OptionContinuationLine
        TaskLine
        TaskContinuationLine

        What about superclass
        '''
        self._clear_data()
        self.source_text = source_text.rstrip()
        raw_lines = []
        prev_line_obj = None
        for source_line in self.source_text.splitlines():
            line_obj = self.line_factory.make_line(source_line)
            print("raw >>{}".format(line_obj.indent), line_obj.text[:50],
                line_obj.__class__.__name__)
            if isinstance(line_obj, OptionContinuationLine):
                if (isinstance(prev_line_obj, OptionLine) or
                    isinstance(prev_line_obj, OptionContinuationLine)):
                    prev_line_obj.continuation_line_objs.append(line_obj)
                else:
                    msg = 'Bad option line sequence for line "{}"'
                    raise OptionLineError(msg.format(line_obj.text))
            elif isinstance(line_obj, TaskContinuationLine):
                if (isinstance(prev_line_obj, TaskLine) or
                    isinstance(prev_line_obj, TaskContinuationLine)):
                    prev_line_obj.continuation_line_objs.append(line_obj)
                else:
                    msg = 'Bad task line sequence for {} "{}"'
                    raise OptionLineError(msg.format(
                        line_obj.__class__.__name__, line_obj.text))
            else:
                raw_lines.append(line_obj)
                prev_line_obj = line_obj
        print('/1' * 35)
        for obj1 in raw_lines:
            print(obj1.text[:50], obj1.__class__.__name__)
            for cont_line in obj1.continuation_line_objs:
                print("......... {}".format(cont_line.text))
            cont_lines_text = [cont_line.text
                               for cont_line in obj1.continuation_line_objs]
            complete_text = "\n".join([obj1.text] + cont_lines_text)
            print("-" * 45 + " Input text")
            print(complete_text)
            line_obj = self.line_factory.make_line(complete_text)
            self._obj_lines.append(line_obj)
            if isinstance(line_obj, OptionLine):
                self._check_for_option_duplication(line_obj)
            elif isinstance(line_obj, TaskLine):
                self.tasks.append(line_obj)
            print("{} Output text, plus {} spaces indent".format(
                "-" * 45, line_obj.indent))
            print(line_obj.text)
            print("." * 75)
        print('\\2' * 35)

        # def _process_buffer(self, buffer_lines):
        #      if buffer_lines is None:
        #          return  # First time called
        #      complete_line = ''.join(buffer_lines)
        #      line_obj = self.line_factory.make_line(complete_line)
        #      self._obj_lines.append(line_obj)
        #      if isinstance(line_obj, OptionLine):
        #          self._check_for_option_duplication(line_obj)
        # # self.parse_text(source_text)
        # complete_line = "\n".join()

        self._calc_maximum_key_length()

    # def parse_text(self, source_text):
    #     self._clear_data()
    #     self.source_text = source_text.rstrip()

    #     for source_line in self.source_text.splitlines():
    #         line_obj = OptionLineFactory()
    #     # source_lines_gen = (line.strip()
    #     #                     for line in self.source_text.splitlines())
    #     buffer_lines = None
    #     for source_line in self.source_text.splitlines():
    #         if source_line.lstrip().startswith(OPT_CONTIN_CHAR):
    #             if not buffer_lines:
    #                 msg = "You can't start text with '{}': {}"
    #                 raise OptionLineError(msg.format(OPT_CONTIN_CHAR,
    #                                                  source_line))
    #             buffer_lines.append(source_line.rstrip())
    #         else:
    #             # Current is non-continuation line, so process buffer_lines
    #             self._process_buffer(buffer_lines)
    #             buffer_lines = [source_line.rstrip()]
    #     self._process_buffer(buffer_lines)
    #     self._calc_maximum_key_length()

    def _calc_maximum_key_length(self):
        """Each line objects needs to know the maximum key length from all
        the option lines, to be able to calculate the "::" indent."""
        try:
            self.max_key_length = max(len(key)
                                      for key in self.option_keys.keys())
            # for line_obj in self.option_keys.values():
            #     line_obj.max_key_length = self.max_key_length
        except ValueError:
            # self.option_keys may be an empty dictionary
            self.max_key_length = 0

    def _check_for_option_duplication(self, line_obj):
        if line_obj.key in self.option_keys:
            msg = 'Duplicate option keys found: "{}"'
            raise OptionLineError(msg.format(line_obj.key))
        else:
            self.option_keys[line_obj.key] = line_obj
            for opt in line_obj.options:
                try:
                    prev_key = self.all_options[opt]
                    msg = 'Duplicate options for different keys ' + \
                          '("{0}{3}{1}" and "{2}{3}{1}")'
                    raise OptionLineError(msg.format(
                        line_obj.key, opt, prev_key,
                        KEY_OPTIONS_SEPARATOR))
                except KeyError:
                    # This is the normal path
                    self.all_options[opt] = line_obj

    def _clear_data(self):
        self._obj_lines = []
        self.option_keys = {}
        self.all_options = {}

    def _process_buffer(self, buffer_lines):
        if buffer_lines is None:
            return  # First time called
        complete_line = ''.join(buffer_lines)
        line_obj = self.line_factory.make_line(complete_line)
        self._obj_lines.append(line_obj)
        if isinstance(line_obj, OptionLine):
            self._check_for_option_duplication(line_obj)


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

TO-DO after all working:
[ ] Continuation lines


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
        self.parse_line()

    @abstractmethod
    def validates(self):
        pass

    # @abstractmethod
    # def parse_text(self, source_text):
    #     pass

    def parse_line(self):
        pass


class BlankLine(BaseOptionLine):

    def validates(self):
        return not len(self.text) and not self.indent


class CommentLine(BaseOptionLine):
    """Any line whose first non-white-space char is '#'
    """

    def validates(self):
        """True if the source_line is a comment"""
        return self.text.startswith("#")


class TaskLine(BaseOptionLine):
    """ Line that begins with '[' and ']' within the first 6 chars,
        to form a status box.
    e.g.
          [ ] Fix the bathroom door
        * [>] Apply for deed of variation
        + [x] Contact agency re contract
    """

    def validates(self):
        """Return True if the source_line is a task."""
        try:
            return self.text[:5].index('[') < self.text[:6].index(']')
        except ValueError:
            # At least one of the brackets is missing
            return False


class OptionLine(BaseOptionLine):
    """A line that has a key, then the double colon, with 0 to many options
    """

    # def __init__(self, source_line=""):
    #     super(OptionLine, self).__init__(source_line)
    def parse_line(self):
        try:
            split_text = self.text.split(KEY_OPTIONS_SEPARATOR, 1)
            self.key, opts = [x.strip() for x in split_text]
            # This is an OptionLine: check that key is a single word
            if len(self.key.split()) != 1:
                msg = 'Bad key "{}" in line "{}"'
                raise OptionLineError(msg.format(self.key, self.text))
            # self.options = set(z.strip() for z in opts.split('|')
            #                    if len(z.strip()))
            self.options = set(x for x in (z.strip()
                                           for z in opts.split('|'))
                               if len(x))
        except ValueError:
            # KEY_OPTIONS_SEPARATOR was missing, so not an OptionLine
            self.key = None

    def validates(self):
        """This is an OptionLine if we have successfully parsed a key"""
        return bool(self.key)


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
        TaskLine,
        OptionLine,
        OrdinaryLine,  # i.e. anything else
    ]

    def make_line(self, source_line):
        for class_ in self.line_classes:
            line_obj = class_(source_line)
            if line_obj.validates():
                return line_obj
        else:
            msg = 'Unknown line type for option line "{}"'
            raise OptionLineError(msg.format(source_line))


class OptionLines(object):
    """This is a list of consecutive BaseOptionLine objects."""

    def __init__(self, source_text=""):
        self._obj_lines = []  # Or use a MutableMapping instead
        self.all_keys = {}
        self.all_options = {}
        self.line_factory = OptionLineFactory()


        # self.text = self.source_line.lstrip()
        # self.indent = len(self.source_line) - len(self.text)
        self.parse_text(source_text)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.format_text()

    def format_text(self):
        """Return lines in canonical output form"""
        output_lines = []
        for line in self._obj_lines:
            output_lines.append(" " * line.indent + line.text)
        return "\n".join(output_lines)

    @property
    def lines(self):
        return self.format_text().splitlines()

    # def _parse_source(self

    def parse_text(self, source_text):
        self._clear_data()
        self.source_text = source_text.rstrip()

        for source_line in self.source_text.splitlines():
            line_obj = self.line_factory.make_line(source_line.rstrip())
            # import pdb;pdb.set_trace()
            self._obj_lines.append(line_obj)

        # buffer_lines = None
        # for line in source_lines_gen:
        #     if line.startswith('|'):
        #         if not buffer_lines:
        #             raise OptionsLineError("You can't start text with '|'")
        #         buffer_lines.append(line)
        #     else:
        #         # Current is non-continuation line, so process buffer_line
        #         self._process_buffer(buffer_lines)
        #         buffer_lines = [line]
        # self._process_buffer(buffer_lines)


    def _clear_data(self):
        self._obj_lines = []
        self.all_keys = {}
        self.all_options = {}


# for source_line in source_text.rstrip().splitlines():
#         line_obj = factory.make_line(source_line)
#         class_names.append(line_obj.__class__.__name__)

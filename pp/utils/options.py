# -*- coding: utf-8 -*-
# pp/utils/options.py

"""
Options format is designed to make reading/writing data simple.
Features:
    Options separated by vertical bar.
    Options should be unique between keys, not just within one key.
    Vertical bar starts continuation line
    Options in each lines sorted
    Line order and blank lines preserved
    Comments preserved

Example data for TaskNav environment file:

    # environment.txt
    # For ease of reading and editing, using options format.

    availability : am | eve | pm
    importance   : a | b | c
    internet     : connected | offline
    location     : banbury | isleworth | kings-sutton | south-bank-centre
                   | whitnash
    # Status uses words rather than dates now
    status       : queued | started | nearly-done | finished | on-hold
    supermarket  : morrisons | sainsburys | tesco
    urgency      : sometime | this-month | this-week | today | tomorrow
    weather      : fine | rain | showers
"""

from pprint import pprint


class OptionLineError(Exception):
    pass


class OptionsList(object):

    def __init__(self, source_text="", max_line_length=60):
        self.max_line_length = max_line_length
        self._lines = []
        self.options = {}
        self.rev_options = {}  # This is a reverse dictionary of self.options
        self.parse_text(source_text)

    def __str__(self):
        return self.format_text()

    @property
    def lines(self):
        return self.format_text().splitlines()

    def format_text(self, max_line_length=None):
        """Prepare text for output in standard format. This is a public
        function, to allow for various output max_line_lengths.
        """
        if max_line_length is None:
            max_line_length = self.max_line_length
        lines_out = []
        try:
            max_key_length = max(len(key) for key in self.options.keys())
        except ValueError:
            # self.options may be an empty dictionary
            max_key_length = 0
        # Allow 3 chars for " : " in between key and options
        max_option_length = max_line_length - max_key_length - 3
        for line in self._lines:
            if not line or line.startswith('#'):
                lines_out.append(line)
            else:
                key, option_str = line.split(':', 1)
                continuation_lines = []
                if len(option_str) > max_option_length:
                    lines = self._split_options(option_str,
                                                max_option_length)
                    option_str = lines[0]
                    continuation_lines = lines[1:]
                new_line = "{1:{0}} : {2}".format(max_key_length,
                                                  key, option_str)
                lines_out.append(new_line)
                for cont_line in continuation_lines:
                    new_line2 = "{1:{0}}   {2}".format(max_key_length,
                                                      "", cont_line)
                    lines_out.append(new_line2)
        return "\n".join(lines_out)

    def parse_text(self, source_text):
        self._clear_data()
        self.source_text = source_text.strip()
        source_lines_gen = (line.strip()
                            for line in self.source_text.splitlines())
        buffer_lines = None
        for line in source_lines_gen:
            if line.startswith('|'):
                if not buffer_lines:
                    raise OptionLineError("You can't start text with '|'")
                buffer_lines.append(line)
            else:
                # Current is non-continuation line, so process buffer_line
                self._process_buffer(buffer_lines)
                buffer_lines = [line]
        self._process_buffer(buffer_lines)

    def part_of(self, outer_opt_list):
        """Return True if all option keys are found in outer_opt_list,
        and for each key, the options are in the outer_opt_list options.
        """
        for key, inner_options in self.options.iteritems():
            try:
                outer_options = outer_opt_list.options[key]
                if not inner_options.issubset(outer_options):
                    return False
            except KeyError:
                return False
        else:
            return True

    # @property
    # def text(self):
    #     return self.format_text()

    def _clear_data(self):
        self._lines = []
        self.options = {}
        self.rev_options = {}  # This is a reverse dictionary of self.options

    def _parse_line(self, line):
        """Expecting one key word before the colon, and options after.
        Ignore duplicate or blank options.
        """
        try:
            key, opts = (x.strip() for x in line.split(':', 1))
            if len(key.split()) != 1:
                msg = 'Bad key "{}" in line "{}"'
                raise OptionLineError(msg.format(key, line))
        except ValueError:
            msg = '":" needed in line "{}"'
            raise OptionLineError(msg.format(line))
        #
        opts_set = set(z.strip() for z in opts.split('|') if len(z.strip()))
        return key, opts_set

    def _process_buffer(self, buffer_lines):
        if buffer_lines is None:
            return  # First time called
        line = ''.join(buffer_lines)
        # Pass through blank lines and comments
        if not line or line.startswith('#'):
            self._lines.append(line)
        else:
            key, opts_set = self._parse_line(line)
            self.options[key] = opts_set
            for opt in opts_set:
                try:
                    prev_key = self.rev_options[opt]
                    msg = 'Duplicate options for different keys ' + \
                          '("{0}:{1}" and "{2}:{1}")'
                    raise OptionLineError(msg.format(key, opt, prev_key))
                except KeyError:
                    # This is the normal path
                    self.rev_options[opt] = key
            option_str = " | ".join(sorted(opts_set))
            self._lines.append("{}:{}".format(key, option_str))

    def _split_options(self, option_str, max_line_length):
        """Split options into multiple strings to deal with long lists"""
        option_gen = (opt.strip() for opt in option_str.split('|'))
        current_line = []
        current_length = 0
        lines = []
        for opt in option_gen:
            if current_length + len(opt) <= max_line_length:
                current_line.append(opt)
                current_length += len(opt)
            else:
                lines.append(' | '.join(current_line))
                current_line = ['| ' + opt]  # Note leading '|'
                current_length = len(opt)
        if current_line:
            lines.append(' | '.join(current_line))
        return lines


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

    def __init__(self, text):
        # Enforce single trailing new line
        self._source_text = text.strip() + "\n"
        self.lines = []
        self.keys = {}
        self.options = {}  # This is a reverse dictionary of self.keys
        self.parse_lines()

    @property
    def text(self):
        return self.format_text()

    def parse_lines(self):
        source_lines_gen = (line.strip()
                            for line in self._source_text.splitlines())
        self.lines = []
        buffer_lines = None
        for line in source_lines_gen:
            if line.startswith('|'):
                if not buffer_lines:
                    raise OptionLineError("You can't start text with '|'")
                buffer_lines.append(line)
            else:
                # Current is non-continuation line, so process buffer_line
                self.process_buffer(buffer_lines)
                buffer_lines = [line]
        self.process_buffer(buffer_lines)

    def _parse_line(self, line):
        try:
            key, opts = (x.strip() for x in line.split(':', 1))
        except ValueError:
            msg = 'One ":" needed in line "{}"'
            raise OptionLineError(msg.format(line))
        options = set(z.strip() for z in opts.split('|'))
        return key, options

    def process_buffer(self, buffer_lines):
        if buffer_lines is None:
            # First time called
            return
        line = ''.join(buffer_lines)
        # Pass through blank lines and comments
        if not line or line.startswith('#'):
            self.lines.append(line)
        else:
            key, options = self._parse_line(line)
            self.keys[key] = options
            for opt in options:
                try:
                    prev_key = self.options[opt]
                    msg = 'Duplicate options for different keys ' + \
                          '("{0}:{1}" and "{2}:{1}")'
                    raise OptionLineError(msg.format(key, opt, prev_key))
                except KeyError:
                    # This is the normal path
                    self.options[opt] = key
            option_str = " | ".join(sorted(options))
            self.lines.append("{}:{}".format(key, option_str))

    def format_text(self):
        """Prepare text for output in standard format.
        """
        lines_out = []
        max_key_length = max(len(key) for key in self.keys.keys())
        for line in self.lines:
            if not line or line.startswith('#'):
                lines_out.append(line)
            else:
                key, options = line.split(':')
                new_line = "{1:{0}} : {2}".format(max_key_length,
                                                  key, options)
                lines_out.append(new_line)
        return "\n".join(lines_out) + "\n"
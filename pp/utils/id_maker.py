# -*- coding: utf-8 -*-
# src/pp-utils/pp/utils/id_maker.py

import uuid
import base64
import re

# Looking for words, with possible embedded ' and _
re_split_words = re.compile(r"[\w'_]+")



"""Make an ID that is both readable and scalable.

We avoid just using a UUID as being unreadable. However, a sequential
number requires access to a central server to allocate the next ID,
giving a single point of failure.

The structure of the ID is in three parts, separated by hyphens.
The supplied prefix could also be made uup of parts, such as
a company prefix, and an abbreviation for the object type.

<prefix>-<readable string>-<uuid>
e.g. a PythonPro ID for a security could be
    pp-sec-3445-8d14e54304de464497153f44a4088f98
    pp-sec-voda-7bfec1a5d6b84703af918bee93000606
"""

# ------------------------------------------------------------------------
# Name shortening, for greater ID readability
# ------------------------------------------------------------------------

# Supply a list of common words to be ignored in making a symbol
hihat_stop_words = [
    "company",
    "corp",
    "corporation",
    "holdings",
    "inc",
    "incorporated",
    "international",
    "limited",
    "ltd",
]


# Supply a dictionary of known abbreviations that will be supplied,
# instead of the rule-based compression.
hihat_known_abbreviations = dict(
    amazon="amzn",
    apple="aapl",
    microsoft="msft",
)

# TO-DO: Force known_abbreviations into lower case
# TO-DO: Multiple characters from multiple words

def hihat(long_name, short_name_length=4,
          stop_words=None, known_abbreviations=None):
    """Reduce a long name to a short symbol, to make it easier to
    recognise in a generated uuid. Very short names are padded with 'x'/

    e.g.  Vodafone --> voda
          BMW      --> bmwx

    The stop words are those that add nothing to the meaning of the name.
    Known abbreviations can be supplied.

    Pun warning! symbol --> cymbal --> hihat.
    """
    if not stop_words:
        stop_words = set(hihat_stop_words)

    if not known_abbreviations:
        known_abbreviations = hihat_known_abbreviations

    vowels = 'aeiou'
    words_in_name = re_split_words.findall(long_name.lower())
    significant_words = [word for word in words_in_name
                         if word not in stop_words]
    # If the abbreviation of the first word is already known, use it
    try:
        return known_abbreviations[significant_words[0]]
    except (KeyError, IndexError):
        if len(significant_words) >= 3:
            # Use initial letters
            chars = [word[0] for word in significant_words]
        else:
            # Ignore vowels from third vowel onwards
            chars = []
            vowel_count = 0
            # Here, there are either one or two significant words
            for char in ''.join(significant_words):
                if char in vowels:
                    vowel_count += 1
                    if vowel_count > 2:
                        continue
                chars.append(char)
        # Having more than two padding chars would mean the name was
        # fewer than two chars.
        chars = chars + ['x'] * short_name_length
        return ''.join(chars)[:short_name_length]

# ------------------------------------------------------------------------
# Generator-based number persistence for ID generation
# ------------------------------------------------------------------------

def _num_counter(prefix, start_at, name_length, separator):
    """Use a coroutine for storing state between calls. So if numbers
    are required, they can be sequential.
    """
    counter = start_at
    name_or_number = yield "Ignore this first result"
    while True:
        if name_or_number:
            try:
                # Check for non-zero integer input
                readable = str(name_or_number + 0).zfill(name_length)
                counter = name_or_number
            except TypeError:
                readable = hihat(name_or_number, name_length)
        else:
            # Default to using the integer incremented
            readable = str(counter).zfill(name_length)
        # yield returns the formatted string,
        # then receives the name_or_number. See PEP 342.
        name_or_number = yield "{}{}{}{}{}".format(
            prefix, separator,
            readable, separator,
            uuid_base64(),
        )
        if not name_or_number:
            counter += 1


def id_generator(prefix, start_at=1, name_length=6, separator='-'):
    """Wrapper for generator, to get while loop started, throwing
    away the first result.
    Return the generator's send method, which must take one argument.
    """
    counter_gen = _num_counter(prefix, start_at, name_length, separator)
    ignored_first_result = next(counter_gen)
    return counter_gen.send

# ------------------------------------------------------------------------
# base64 handling to compress UUID string from 36 to 22 characters
# ------------------------------------------------------------------------

def uuid2slug(uuidstring):
    """Convert 36-char UUID to 22-char base64 string, changing
    "+" to "$" and "/" to "_".
    """
    uuid_bytes = uuid.UUID(uuidstring).bytes
    return base64.b64encode(uuid_bytes, '$_').rstrip('=\n')


def slug2uuid(slug):
    """Convert 22-char base64 string to 36-char UUID, changing
    "$" back to "+" and "_" to "/". Create uuid and back to string,
    to ensure slug is valid.
    """
    uuid_bytes = base64.b64decode(slug + '==', '$_')
    return str(uuid.UUID(bytes=uuid_bytes))


def uuid_base64():
    """Generate a UUID, as a 22-char string"""
    return uuid2slug(uuid.uuid4().hex)


if __name__ == '__main__': #pragma nocover
    print("Starting...\n")

    id_gen_usr = id_generator('pp-usr', start_at=345)
    for val in [0, 5001, 0, "John Smith", 0, 201, 0, "Vodafone", 0, 0]:
        print("{:>12} --> {}".format(val, id_gen_usr(val)))

    print("\nFinished.")
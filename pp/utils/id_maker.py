# -*- coding: utf-8 -*-
# src/pp-utils/pp/utils/id_maker.py

import uuid
import base64
import re
##import random

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


def hihat(long_name, short_name_length=4,
          stop_words=None, known_abbreviations=None):
    # TO-DO
    """Reduce a long name to a short symbol, to make it easier to
    recognise in a generated uuid. Very short names are padded with 'x'/

    e.g.  Vodafone --> voda
          BMW      --> bmwx

    The stop words are those that add nothing to the meaning of the name.
    Known abbreviations can be supplied.

    Pun warning: symbol --> cymbal --> hihat.
    """
    if not stop_words:
        stop_words = set(hihat_stop_words)
    # TO-DO: Force known_abbreviations into lower case
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


def num_counter(prefix, start_at, name_length, separator):
    """Use a coroutine for storing state between calls. So if numbers
    are required, they can be sequential.
    """
##    yield None
    counter = start_at
    name_or_number = yield None
    while True:
        # yield a value and receive a new one. See PEP 342
        # other = yield foo
        # "yield foo and, when a value is sent to me,
        # set other to that value."
        #incoming_sent_value_ignored = yield value
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
    ctr = num_counter(prefix, start_at, name_length, separator)
    next(ctr)
    return ctr.send


def uuid2slug(uuidstring):
    """Convert 36-char UUID to 22-char base64 string, changing
    "+" to "$" and "/" to "_".
    See
        http://stackoverflow.com/questions/12270852/
               convert-uuid-32-character-hex-string-into-a-youtube-
               style-short-id-and-back
"""
    uuid_bytes = uuid.UUID(uuidstring).bytes
    return base64.b64encode(uuid_bytes, '$_').rstrip('=\n')

##    raw_slug = uuid.UUID(uuidstring).bytes.encode('base64')
##
##    return raw_slug.rstrip('=\n').replace('+', '$').replace('/', '_')


def slug2uuid(slug):
    """Convert 22-char base64 string to 36-char UUID, changing
    "$" back to "+" and "_" to "/". Create uuid and back to string,
    to ensure slug is valid.
    """
    uuid_bytes = base64.b64decode(slug + '==', '$_')
    return str(uuid.UUID(bytes=uuid_bytes))

    raw_slug = (slug + '==').replace('_', '/').replace('$', '+')
    return str(uuid.UUID(bytes=raw_slug.decode('base64')))


def uuid_base64():
    """Generate a UUID, as a 22-char string"""
    return uuid2slug(uuid.uuid4().hex)



if __name__ == '__main__':
    print("Starting...\n")

##    u = str(uuid.uuid4())
##    print(u)
##    s = uuid2slug(u)
##    print(s)
##    u2 = slug2uuid(s)
##    assert u2 == u
    # Set random seed, so random uuids are repeatable
##    random.seed(123)

    id_gen_usr = id_generator('rd-usr', start_at=345)
    for val in [0, 5001, 0, "John Smith", 0, 201, 0, "Vodafone", 0, 0]:
        print("{:>12} --> {}".format(val, id_gen_usr(val)))

    import base64
    base64.urlsafe_b64encode

##    id_gen = id_generator('rd', 'sec', 101)
##    for num, txt in enumerate(["", None, "one", "two", 103,
##                               "", None, "", "four"]):
##        print('{:3}:   "{:6}" --> "{}"'.format(num, txt, id_gen(txt)))

##    long_name = 'Robert Paul Collins'
##    short_name_length = 12
##    res = hihat(long_name, short_name_length)
##    print("{} --> {}".format(long_name, res))

    print("\nFinished.")
# -*- coding: utf-8 -*-
# src/pp-utils/pp/utils/id_maker.py

import uuid


def foo99():
    assert 0


class ID(object):
    """Make an ID that is both readable and scalable.

    We avoid just using a UUID as being unreadable. However, a sequential
    number requires access to a central server to allocate the next ID,
    giving a single point of failure.

    The structure of the ID is in four parts, separated by hyphens.

    <company prefix>-<object type prefix>-<readable string>-<uuid>
    e.g. a PythonPro ID for a security could be
        pp-sec-3445-8d14e54304de464497153f44a4088f98
        pp-sec-voda-7bfec1a5d6b84703af918bee93000606
    """

    def __call__(self):
        return 99

def num_counter(company_prefix, type_prefix, start_number):
    """Use a coroutine for storing state between calls. So if numbers
    are required, they can be sequential.
    """
    yield None
    counter = start_number
    short_name = ""
    while True:
        # yield a value and receive a new one. See PEP 342
        # other = yield foo
        # "yield foo and, when a value is sent to me,
        # set other to that value."
        #incoming_sent_value_ignored = yield value
        try:
            readable = short_name[::-1] if short_name else counter
        except TypeError:
            # Deal with non-zero integer input
            readable = int(short_name)
            counter = readable
        short_name = yield "{}-{}-{}-{}".format(
            company_prefix,
            type_prefix,
            readable,
            uuid_base64(),
        )
        if not short_name:
            counter += 1


def id_generator(company_prefix, type_prefix, start_number=1):
    ctr = num_counter(company_prefix, type_prefix, start_number)
    next(ctr)
    return ctr.send


def uuid2slug(uuidstring):
    """Convert 36-char UUID to 22-char base64 string.
    See
        http://stackoverflow.com/questions/12270852/
               convert-uuid-32-character-hex-string-into-a-youtube-
               style-short-id-and-back
"""
    raw_slug = uuid.UUID(uuidstring).bytes.encode('base64')
    return raw_slug.rstrip('=\n').replace('+', '-').replace('/', '_')


def slug2uuid(slug):
    """Convert 22-char base64 string to 36-char UUID"""
    raw_slug = (slug + '==').replace('_', '/').replace('-', '+')
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

    id_gen = id_generator(101)
    for num, txt in enumerate(["", None, "one", "two", "three",
                               "", None, "", "four"]):
        print('{:3}:   "{:6}" --> "{}"'.format(num, txt, id_gen(txt)))

    print("\nFinished.")
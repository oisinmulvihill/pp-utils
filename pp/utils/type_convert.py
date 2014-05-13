# -*- coding: utf-8 -*-
# pp-utils/pp/utils/type_convert.py


def force_to_set(value):
    """Take set, list, string, integer and return a set"""

    try:
        # Is value a set?
        value_set = value | set()
    except TypeError:
        try:
            # Is value a list?
            value_set = set(value + [])
        except TypeError:
            # Whatever else it is, put it in a set
            value_set = set([value])
    return value_set


if __name__ == '__main__':
    pass

    # import pdb; pdb.set_trace()
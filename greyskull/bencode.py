# -*- coding: utf-8 -*-
"""
Bencode encoding code by Petru Paler, slightly simplified by uriel, additionally
modified by Carlos Killpack
"""

from itertools import chain


def bencode(x):
    r = []
    if isinstance(x, (int, long, bool)):
        r.extend(('i', str(x), 'e'))
    elif isinstance(x, str):
        r.extend((str(len(x)), ':', x))
    elif isinstance(x, (list, tuple)):
        r.append('l')
        r.extend(bencode(i) for i in x)
        r.append('e')
    elif isinstance(x, dict):
        for key in x.iterkeys():
            if isinstance(key, int):
                raise TypeError
        r.append('d')
        ilist = x.items()
        ilist.sort()
        flist = tuple((bencode(k), bencode(v)) for k, v in ilist)
        r.extend(tuple(chain(*flist)))
        r.append('e')
    return ''.join(r)

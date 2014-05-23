# -*- coding: utf-8 -*-
"""
Memcached namespaces:
    - 'T': Keys / info_hashes -> 'Compact' style string of binary encoded ip+ports
    - 'K': Keys / info_hashes -> String of | delimited peer-hashes DEPRECATED
    - 'I': peer-hash -> Metadata string: 'ip|port' DEPRECATED
    - 'P': peer-hash -> Anything 'true'. TODO: Should be a 'ref count'.
    - 'S': "%s!%s" (Keys/info_hash, param) -> Integer
    - 'D': Debug data

A peer hash is: md5("%s/%d" % (ip, port)).hexdigest()[:16]

This allows peer info to be shared and decay by itself, we will delete
references to peer from the key namespace lazily.

MAKE SURE YOU REFER TO doc/ntrack.rst FOR CONSISTENCY!
"""

from tornado.web import RequestHandler

from greyskull.memcache import (get,
                                set as mset,
                                get_multi,
                                delete as mdel,
                                incr,
                                decr, )


class NTrack(RequestHandler):
    STATS = True
    ERRORS = True
    INTERVAL = 18424  # ???
    MEMEXPIRE = 60 * 60 * 24 * 2  # ???
    PEER_SIZE = 6
    MAX_PEERS = 32
    MAX_PEER_SIZE = PEER_SIZE * MAX_PEERS
    def get(self, key):
        pass

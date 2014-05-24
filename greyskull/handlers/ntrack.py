# -*- coding: utf-8 -*-
"""
Memcached namespaces:
    - 'T': Keys / info_hashes -> 'Compact' style string of binary encoded ip+ports
    - 'K': Keys / info_hashes -> String of | delimited peer-hashes DEPRECATED
    - 'I': peer-hash -> Metadata string: 'ip|port' DEPRECATED
    - 'P': peer-hash -> Anything 'true'. TODO: Should be a 'ref count'.
    - 'S': "%s!%s" (Keys/info_hash, param) -> Integer
    - 'D': Debug data

A peer hash is: sha1("%s/%d" % (ip, port)).hexdigest()[:16]

This allows peer info to be shared and decay by itself, we will delete
references to peer from the key namespace lazily.

MAKE SURE YOU REFER TO doc/ntrack.rst FOR CONSISTENCY!
"""

from hashlib import sha1

from urllib.parse import urlencode

from tornado import web

from greyskull.bencode import bencode

from greyskull.storage import (get,
                               set as mset,
                               get_multi,
                               delete as mdel,
                               incr,
                               decr, )


class BTCompat(web.RequestHandler):
    """
    Handles bittorrent-specific tracker requests
    """
    def get(self):
        try:
            info_hash = self.get_argument('info_hash')
        except web.MissingArgumentError:
            self.redirect('/')
        else:
            args = dict(event=self.get_argument('event', default=None),
                        left=self.get_argument('left', default=None))
            self.redirect('/ntrk/%s?%s' % (info_hash, urlencode(args)))


class NTrack(web.RequestHandler):
    STATS = True
    ERRORS = True
    INTERVAL = 18424  # ???
    MEM_EXPIRE = 60 * 60 * 24 * 2  # ???
    PEER_SIZE = 6
    MAX_PEERS = 32
    MAX_PEER_SIZE = PEER_SIZE * MAX_PEERS

    def initialize(self, port):
        self.port = port

    def _update_stats(self, key,
                      new_track=False, lost_peers=0,
                      event=None, left=None):
        if not self.STATS:
            return
        complete = '%s!complete' % key
        incomplete = '%s!incomplete' % key
        if new_track:
            mset(complete, '0', namespace='S')
            mset(incomplete, '0', namespace='S')
        elif lost_peers:
            decr(incomplete, lost_peers, namespace='S')
        elif event in ('stopped', 'started'):
            if left == '0':
                decr(complete, namespace='S')
            else:
                decr(incomplete, namespace='S')
        elif event in ('completed', ):
            decr(incomplete, namespace='S')
            incr(complete, namespace='S')

    def get(self, key):
        if len(key) > 128:
            pass  # TODO Insanely long key, let them know
        phash = sha1("%s/%d" % (self.request.remote_ip, self.port)).hexdigest()[:16]
        event = self.get_argument('event', default=None)
        left = self.get_argument('left', default=None)
        if event == 'stopped':
            mdel(phash, namespace='P')
            self._update_stats(key, event=event, left=left)
            self.write(bencode({'interval': self.INTERVAL,
                                'peers': []}))
        elif event == 'completed':
            self._update_stats(key, event=event, left=left)
        elif event == 'started':
            self._update_stats(key, event=event, left=left)
        peer_list = get(key, namespace='T')
        if peer_list:
            res = ''
        else:
            peer_list = res = ''
            self._update_stats(key, new_track=True)
        if not phash in peer_list:
            mset(phash, 1, namespace='P')
            peer_list += phash
            mset(key, peer_list, namespace='K')
        if self.STATS:
            self.write(bencode({'interval': self.INTERVAL,
                                'peers': res,
                                'complete': get('%s!complete' % key, namespace='S') or 0,
                                'incomplete': get('%s!incomplete' % key, namespace='S') or 0}))
        else:
            self.write(bencode({'interval': self.INTERVAL,
                                'peers': res}))
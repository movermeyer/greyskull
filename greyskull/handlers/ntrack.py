# -*- coding: utf-8 -*-
"""
NTrack and a Bittorrent compatibility layer
"""

from hashlib import sha1

from urllib.parse import urlencode

from tornado import web

from greyskull.bencode import bencode
from greyskull.ip_utils import encode_host_and_port
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
                        left=self.get_argument('left', default=None), )
            self.redirect('/ntrk/%s?%s' % (info_hash, urlencode(args)))


class NTrack(web.RequestHandler):
    """
    An implementation of the NTrack protocol based on the source of `ATrack`_ and the protocol
    outlined in the `NTrack whitepaper`_. Though technically a fork, I've rewritten nearly
    everything.

    .. _ATrack: http://repo.cat-v.org/atrack/
    .. _NTrack whitepaper: http://repo.cat-v.org/atrack/ntrack
    """
    MEM_EXPIRE = 60 * 60 * 24 * 2  # ???

    # noinspection PyMethodOverriding
    def initialize(self, port, stats, errors, interval):
        self.port = int(port)
        self.stats = bool(stats)
        self.errors = bool(errors)
        self.interval = int(interval)

    def _update_stats(self, key, new_track=False, lost_peers=0, event=None, left=None) -> None:
        if not self.stats:
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

    def _peer_hash(self, ip: str, port: int or None=None) -> str:
        if port is None:
            port = self.port
        return sha1("%s/%d" % (ip, port)).hexdigest()[:16]

    def get(self, key: str):
        """
        Memcached namespaces:
            - 'K' -> key: [peer_hash: str, ...]
            - 'P' -> peer_hash: (ip: str, port: int)
            - 'S' -> "%s!%s" % (key: str, param: str): int
            - 'D' -> Debug data

        This allows peer info to be shared and decay by itself, we will delete
        references to peers from the key namespace lazily.

        MAKE SURE YOU REFER TO doc/NTrack.rst FOR CONSISTENCY!

        :param key:
        :return:
        """
        if len(key) > 128:
            pass  # TODO Insanely long key, let them know
        peer_hash = self._peer_hash(self.request.remote_ip)
        event = self.get_argument('event', default=None)
        left = self.get_argument('left', default=None)
        if event == 'stopped':
            mdel(peer_hash, namespace='P')
            self._update_stats(key, event=event, left=left)
            self.write(bencode({'interval': self.interval,
                                'peers': []}))
        elif event == 'completed':
            self._update_stats(key, event=event, left=left)
        elif event == 'started':
            self._update_stats(key, event=event, left=left)
        peer_list = get(key, namespace='K')
        if peer_list:
            if peer_hash in peer_list:
                peer_list.remove(peer_hash)
            peers = get_multi(peer_list, namespace='P')
            lost_peers = [p_hash for p_hash, peer in zip(peer_list, peers) if peer is None]
            if lost_peers:
                for lost_peer in lost_peers:
                    pass
            res = [encode_host_and_port(peer[0], peer[1]) for peer in peers]
        else:
            peer_list = res = []
            self._update_stats(key, new_track=True)
        if not peer_hash in peer_list:
            mset(peer_hash, (self.request.remote_ip, self.port), namespace='P')
            peer_list.append(peer_hash)
        mset(key, peer_list, namespace='K')
        if self.stats:
            self.write(bencode({'interval': self.interval,
                                'peers': res,
                                'complete': get('%s!complete' % key, namespace='S') or 0,
                                'incomplete': get('%s!incomplete' % key, namespace='S') or 0}))
        else:
            self.write(bencode({'interval': self.interval,
                                'peers': res}))

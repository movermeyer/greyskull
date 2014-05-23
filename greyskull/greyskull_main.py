#!/usr/bin/env python3
"""
An ntrack tracker
=================
http://repo.cat-v.org/atrack/


"""
from os import environ

# We do cherrypy now
from cgi import parse_qs

from bencode import bencode

from struct import pack

from random import randrange

# TODO: Decide if I want to switch to redis
from google.appengine.api.memcache import get
from google.appengine.api.memcache import set as mset
from google.appengine.api.memcache import get_multi
from google.appengine.api.memcache import delete as mdel
from google.appengine.api.memcache import incr, decr

# Set to false if you don't want to keep track of the number of
# seeders and leechers
STATS = True
# If false we don't bother report errors to clients to save(?)
# bandwith and CPU
ERRORS = True
INTERVAL = 18424
# When to expire peers from memcache?
MEMEXPIRE = 60*60*24*2

def resps(string):
    """Sends out a response?"""
    print "Content-type: text/plain"
    print ""
    print string, # Make sure we don't add a trailing new line!

def prof_main():
    """This is the main function for profiling"""
    import cProfile, pstats, StringIO
    import logging
    prof = cProfile.Profile()
    prof = prof.runctx("real_main()", globals(), locals())
    stream = StringIO.StringIO()
    stats = pstats.Stats(prof, stream=stream)
    stats.sort_stats("time")  # Or cumulative
    stats.print_stats(80)  # 80 = how many to print
    # The rest is optional.
    stats.print_callees()
    stats.print_callers()
    logging.info("Profile data:\n%s", stream.getvalue())


def real_main():
    """The real shit"""
    args = parse_qs(environ['QUERY_STRING'])

    if not args:
        print "Status: 301 Moved Permanantly\nLocation: /\n\n",
        return

    for arg in ('info_hash', 'port'):
        if arg not in args or len(args[arg]) != 1:
            if ERRORS:
                resps(bencode({'failure reason': "You must provide %s!" % arg}))
            return

    key = args['info_hash'][0]
    if STATS:
        key_complete = '%s!complete' % key
        key_incomplete = '%s!incomplete' % key
    left = args.pop('left', [None])[0]
    err = None

    if(len(key) > 128):
        err = "Insanely long key!"
    else:
        try:
            port = int(args['port'][0])
            if port > 65535 or port < 1:
                err = "Invalid port number!"
        except:
            err = "Invalid port number!"

    if err:
        if ERRORS:
            resps(bencode({'failure reason': err}))
        return

    # Crop raises chance of a clash, plausible deniability for the win!
    # XXX TODO Instead of a hash, we should use the packed ip+port
    #phash = md5("%s/%d" % (ip, port)).hexdigest()[:16]
    # TODO check that it is a v4 address
    i = environ['REMOTE_ADDR'].split('.')
    phash = pack('>4BH', int(i[0]), int(i[1]), int(i[2]), int(i[3]), port)
    # TODO BT: If left=0, the download is done and we should not
    # return any peers.
    event = args.pop('event', [None])[0]
    if event == 'stopped':
        # Maybe we should only remove it from this track, but
        # this is good enough.
        mdel(phash, namespace='P')
        if STATS:
            # XXX Danger of incomplete underflow!
            if left == '0':
                decr(key_complete, namespace='S')
            else:
                decr(key_incomplete, namespace='S')

        return # They are going away, don't waste bw/cpu on this.
        #resps(bencode({'interval': INTERVAL, 'peers': []}))

    elif STATS and event == 'completed':
        decr(key_incomplete, namespace='S')
        incr(key_complete, namespace='S')

    updatetrack = False

    # Get existing peers

    peer_size = 6
    max_peers = 32
    max_peers_size = max_peers * peer_size
    an_info_hash = get(key, namespace='T')
    # TODO: perhaps we should use the array module:
    # http://docs.python.org/library/array.html

    if an_info_hash:
        als = [an_info_hash[x:x + peer_size] for x in xrange(0, l, peer_size)]
        l = len(als) # how this works?
        if l > max_peers:
            i = randrange(0, l - max_peers)
            ii = i * peer_size
            rs = an_info_hash[ii:ii + max_peers_size]
            rls = als[i:i + max_peers]
        else:
            rs = an_info_hash
            rls = als

        rrls = get_multi(rls, namespace='P').keys()

        # NOTE Do not use a generator, generators are always true even if empty!
        lostpeers = [p for p in rls if p not in rrls] 
        if lostpeers: # Remove lost peers
            rs = ''.join(rrls)

            for peer in lostpeers:
                if peer in als:
                    als.remove(peer)

            an_info_hash = ''.join(als)

            updatetrack = True
            if STATS:
                # XXX medecau suggests we might use len(s) instead 
                # of counting leechers.
                # XXX If we underflow, should decrement from '!complete'
                decr(key_incomplete, len(lostpeers), namespace='S') 

        # Remove self from returned peers
        # XXX Commented out as we are shorter on CPU than bw
        #if phash in peers:
        #    peers.pop(phash, None) 

    # New track!
    else:
        an_info_hash = rs = ''
        als = []
        if STATS:
            mset(key_complete, '0', namespace='S')
            mset(key_incomplete, '0', namespace='S')

    if phash not in als: # Assume new peer
        # XXX We don't refresh the peers expiration date on every request!
        mset(phash, 1, namespace='P') 
        an_info_hash += phash
        updatetrack = True
        if STATS: # Should we bother to check event == 'started'? Why?
            if left == '0':
                incr(key_complete, namespace='S')
            else:
                incr(key_incomplete, namespace='S')

    if updatetrack:
        mset(key, an_info_hash, namespace='K')

    if STATS:
        resps(bencode({'interval':INTERVAL, 'peers':rs,
            'complete':(get(key_complete, namespace='S') or 0),
            'incomplete':(get(key_incomplete, namespace='S') or 0)}))
    else:
        resps(bencode({'interval':INTERVAL, 'peers':rs}))


#MAIN = prof_main
MAIN = real_main

if __name__ == '__main__':
    MAIN()

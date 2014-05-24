# -*- coding: utf-8 -*-

from memcache import Client

mc = Client(['127.0.0.1:11211'], debug=0)

# TODO make this dynamic, I don't want to have to expose each method manually
get = mc.get
set = mc.set
get_multi = mc.get_multi
delete = mc.delete
incr = mc.incr
decr = mc.decr

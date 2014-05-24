# -*- coding: utf-8 -*-

from tornado.web import URLSpec as url

from greyskull.handlers import (NTrack,
                                BTCompat,
                                MemStat,
                                Index,
                                Redirect, )

urlpatterns = [
    url(r'/ntrk/(.*)', NTrack, kwargs=dict(port='80')),  # FIXME
    url(r'/tracker', BTCompat),
    url(r'', MemStat),
    url(r'/', Index),
    url(r'.*', Redirect),
]

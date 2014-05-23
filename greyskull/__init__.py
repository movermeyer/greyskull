# -*- coding: utf-8 -*-
"""
Greyskull: A better ntrack tracker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from tornado.web import Application

from greyskull.urls import urlpatterns

__author__ = "Carlos Killpack"
__email__ = "carlos.killpack@rocketmail.com"
__license__ = "MIT/WTFPL"
__version__ = "0.0.1.dev1"

application = Application(urlpatterns)

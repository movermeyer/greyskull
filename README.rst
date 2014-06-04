|travis_ci| |coveralls| |version|

Greyskull
=========

An NTrack Implementation

Setup Instructions
------------------

Greyskull is configured using the following environment variables:

+-----------------------------------+--------------------------------------------+------------------------+
| Name                              | Description                                | Default                |
+===================================+============================================+========================+
| ``GREYSKULL_EXTERNAL_PORT``       | The internet-facing port that greyskull is | ``80``                 |
|                                   | being served on.                           |                        |
+-----------------------------------+--------------------------------------------+------------------------+
| ``GREYSKULL_MEMCACHED_ENDPOINTS`` | A comma separated list of memcached        | ``'127.0.0.1:11211'``  |
|                                   | endpoints for greyskull to talk to.        |                        |
+-----------------------------------+--------------------------------------------+------------------------+
| ``GREYSKULL_MAX_PEERS``           | The maximum number of peers to return in a | ``32``                 |
|                                   | single request.                            |                        |
+-----------------------------------+--------------------------------------------+------------------------+
| ``GREYSKULL_STATS``               |                                            | ``True``               |
+-----------------------------------+--------------------------------------------+------------------------+
| ``GREYSKULL_ERRORS``              |                                            | ``True``               |
+-----------------------------------+--------------------------------------------+------------------------+
| ``GREYSKULL_INTERVAL``            |                                            | ``18424``              |
+-----------------------------------+--------------------------------------------+------------------------+

As you might know, environment variables must be strings. For the most part this isn't an issue,
except in the case of ``GREYSKULL_STATS`` and ``GREYSKULL_ERRORS`` where a boolean is expected.
In this case use ``1`` for ``True`` and ``0`` for ``False``.

Contact
-------

Carlos Killpack <carlos.killpack@rocketmail.com>

License
-------

All original code is in the public domain, MIT, or ISC at your choice.

The Bencode generation code originally from the standard python bittorrent
implementation is by Petru Paler and under a MIT licenses (AFAIK).


.. |travis_ci| image:: https://travis-ci.org/xj9/greyskull.svg?branch=master
   :target: https://travis-ci.org/xj9/greyskull

.. |coveralls| image:: https://img.shields.io/coveralls/xj9/greyskull.svg
   :target: https://coveralls.io/r/xj9/greyskull

.. |version| image:: https://pypip.in/version/Greyskull/badge.svg
   :target: https://pypi.python.org/pypi/Greyskull/
   :alt: Latest Version

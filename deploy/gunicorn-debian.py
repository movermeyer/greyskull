# -*- coding: utf-8 -*-

CONFIG = {
    'mode': 'wsgi',
    'environment': {
        #'PYTHONPATH': '/path/to/virtualenv
    },
    'args': (
        '--bind=unix:/var/run/gunicorn/greyskull.sock',
        '--workers=4',
        '--worker-class=gevent',
        '--worker-connections=30',
        '--timeout=30',
        'greyskull.wsgi:application'
    )
}

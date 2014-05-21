# -*- coding: utf-8 -*-

CONFIG = {
    'mode': 'wsgi',  # FIXME is this right?
    'environment': {
        #'PYTHONPATH': '/path/to/virtualenv
    },
    'args': (
        '--bind=unix:/var/run/gunicorn/greyskull.sock',
        '--workers=4',
        '--worker-class=tornado',
        '--timeout=30',
        'greyskull:application'
    )
}

'''
    vngshare - Vserver-like Notebook Grader Share
    Similar to vserver; allows easy testing.
'''

import sys

try:
    from .ngshare import main
except ImportError:
    from ngshare import main

if __name__ == '__main__':
    main(
        [
            '--vngshare',
            '--database',
            'sqlite:////tmp/ngshare.db',
            '--storage',
            '/tmp/ngshare',
            '--debug',
        ]
        + sys.argv[1:]
    )

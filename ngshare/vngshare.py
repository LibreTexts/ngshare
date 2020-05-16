'''
    vngshare - Vserver-like Notebook Grader Share
    Similar to vserver; allows easy testing.
'''

import os
import sys

if __name__ == '__main__':  # pragma: no cover
    os.execvp(
        'python3',
        [
            'python3',
            'ngshare.py',
            '--vngshare',
            '--database',
            'sqlite:////tmp/ngshare.db',
            '--storage',
            '/tmp/ngshare',
            '--debug',
        ]
        + sys.argv[1:],
    )

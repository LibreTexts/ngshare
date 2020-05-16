'''
    Test database migration tools
'''

from . import dbutil
import os

def test_update():
    'Test update database'

    # delete database if exist
    try:
        os.unlink(dbutil.DEFAULT_DB)
    except FileNotFoundError:
        pass

    dbutil.upgrade(dbutil.DEFAULT_DB)
    # Downgrade to init
    dbutil.main(['downgrade', 'aa00db20c10a'])
    # Downgrade to nothing
    dbutil.main(['downgrade', 'base'])
    # Offline mode
    dbutil.main(['upgrade', 'head', '--sql'])
    # Upgrade to head
    dbutil.main(['upgrade', 'head'])
    # Invalid argument error
    try:
        dbutil.main([])
    except SystemExit:
        pass

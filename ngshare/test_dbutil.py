'''
    Test database migration tools
'''

import os
import tempfile

from . import dbutil


def test_update():
    'Test update database'
    # Create file name
    tempdb_path = tempfile.mktemp('.db')
    tempdb_url = 'sqlite:///' + tempdb_path
    # Create database
    assert not os.path.exists(tempdb_path)
    dbutil.upgrade(tempdb_url)
    # Downgrade to init
    dbutil.main(['downgrade', 'aa00db20c10a'], tempdb_url)
    # Downgrade to nothing
    dbutil.main(['downgrade', 'base'], tempdb_url)
    # Offline mode
    dbutil.main(['upgrade', 'head', '--sql'], tempdb_url)
    # Upgrade to head
    dbutil.main(['upgrade', 'head'], tempdb_url)
    # Invalid argument error
    try:
        dbutil.main([])
    except SystemExit:
        pass
    # Remove tempdb
    os.remove(tempdb_path)

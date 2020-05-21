'''
    Test database migration tools
'''

import os
import tempfile
import pytest

from . import dbutil


def test_update():
    'Test update database'
    # Create file name
    tempdb_path = tempfile.mktemp('.db')
    tempdb_url = 'sqlite:///' + tempdb_path
    tempdir = tempfile.mkdtemp()
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
    dbutil.main(
        ['-x', 'data=true', '-x', 'storage=' + tempdir, 'upgrade', 'head'],
        tempdb_url,
    )
    # Invalid argument error
    with pytest.raises(SystemExit):
        dbutil.main([])
    # Remove tempdb
    os.remove(tempdb_path)

# TODO: add test cases for data migration


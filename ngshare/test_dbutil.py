'''
    Test database migration tools
'''

import os
import tempfile
from collections import namedtuple
import pytest

from sqlalchemy import create_engine, Column, INTEGER, TEXT
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from . import dbutil


def test_update():
    'Test update database'
    # Create file name
    tempdb_path = tempfile.mktemp('.db')
    tempdb_url = 'sqlite:///' + tempdb_path
    tempdir = tempfile.mkdtemp()
    # Create database
    assert not os.path.exists(tempdb_path)
    CmdOpts = namedtuple('CmdOpts', ['x'])
    cmd_opts = CmdOpts(['data=true', 'storage=' + tempdir])
    dbutil.upgrade(tempdb_url, cmd_opts=cmd_opts)
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
    os.rmdir(tempdir)


def test_add_file_size():
    'Test 1921a169739b_add_file_size.py data migration'
    # Create file name
    tempdb_path = tempfile.mktemp('.db')
    tempdb_url = 'sqlite:///' + tempdb_path
    tempdir = tempfile.mkdtemp()
    # Get to 1 version before
    dbutil.main(['upgrade', '1921a169739b-1'], tempdb_url)
    # Config SQLalchemy
    Base_old = declarative_base()
    Base_new = declarative_base()

    class File_old(Base_old):
        __tablename__ = 'files'
        _id = Column(INTEGER, primary_key=True)
        filename = Column(TEXT)
        checksum = Column(TEXT)
        actual_name = Column(TEXT)

    class File_new(Base_new):
        __tablename__ = 'files'
        _id = Column(INTEGER, primary_key=True)
        filename = Column(TEXT)
        checksum = Column(TEXT)
        size = Column(INTEGER)
        actual_name = Column(TEXT)

    # Add data
    db = sessionmaker(bind=create_engine(tempdb_url))()
    assert len(db.query(File_old).all()) == 0
    db.add(File_old(filename='myfile.txt', actual_name='abcdef.txt'))
    db.add(File_old(filename='dev-null.img', actual_name='ghijkl.img'))
    open(os.path.join(tempdir, 'abcdef.txt'), 'wb').write(b'mycontent')
    open(os.path.join(tempdir, 'ghijkl.img'), 'wb').write(b'')
    assert len(db.query(File_old).all()) == 2
    db.commit()
    db.close()
    # Upgrade
    args = ['-x', 'data=true', '-x', 'storage=' + tempdir]
    dbutil.main(args + ['upgrade', '1921a169739b'], tempdb_url)
    # Check data
    db = sessionmaker(bind=create_engine(tempdb_url))()
    assert dict(
        map(lambda x: (x.filename, x.size), db.query(File_new).all())
    ) == {'myfile.txt': len(b'mycontent'), 'dev-null.img': 0}
    db.close()
    # Downgrade
    dbutil.main(['downgrade', '1921a169739b-1'], tempdb_url)
    # Test when file not found
    os.unlink(os.path.join(tempdir, 'abcdef.txt'))
    dbutil.main(args + ['upgrade', '1921a169739b'], tempdb_url)
    # Check data
    db = sessionmaker(bind=create_engine(tempdb_url))()
    assert dict(
        map(lambda x: (x.filename, x.size), db.query(File_new).all())
    ) == {'myfile.txt': None, 'dev-null.img': 0}
    db.close()
    # Remove tempdb
    os.remove(tempdb_path)
    for i in os.listdir(tempdir):
        os.unlink(os.path.join(tempdir, i))
    os.rmdir(tempdir)

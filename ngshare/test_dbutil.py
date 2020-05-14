'''
    Test database migration tools
'''

from . import dbutil

def test_update():
	'Test update database'
	dbutil.upgrade('sqlite:///ngshare.db')


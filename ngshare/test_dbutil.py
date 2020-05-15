'''
    Test database migration tools
'''

import sys
from . import dbutil

def test_update():
	'Test update database'
	dbutil.upgrade(dbutil.DEFAULT_DB)
	sys_argv = sys.argv
	# Downgrade to init
	sys.argv = ['dbutil.py', 'downgrade', 'aa00db20c10a']
	dbutil.main()
	# Downgrade to nothing
	sys.argv = ['dbutil.py', 'downgrade', 'base']
	dbutil.main()
	# Offline mode
	sys.argv = ['dbutil.py', 'upgrade', 'head', '--sql']
	dbutil.main()
	# Upgrade to head
	sys.argv = ['dbutil.py', 'upgrade', 'head']
	dbutil.main()
	# Invalid argument error
	try:
		sys.argv = ['dbutil.py']
		dbutil.main()
	except SystemExit:
		pass
	sys.argv = sys_argv

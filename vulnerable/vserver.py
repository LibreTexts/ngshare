'''
	Vulnerable server
'''

from app import request, app
import os, sys

BASE_DIR = os.path.dirname(__file__)

from helper import (json_success, json_error, error_catcher, path_modifier,
					get_pathname, remove_pathname)
import helper
import unix		# all unix APIs 
import nbgrader	# all nbgrader APIs

@app.route('/')
@error_catcher
def home_page(deduct=lambda x: False) :
	return open(os.path.join(BASE_DIR, 'home.html')).read()

@app.route('/favicon.ico')
@error_catcher
def favicon() :
	return ''

@app.errorhandler(404)
@error_catcher
def page_not_found(error):
	return json_error('404 (Not Found)')

if __name__ == '__main__' :
	host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
	port = int(sys.argv[2]) if len(sys.argv) > 2 else 11111
	app.run(host=host, port=port, debug=True, threaded=True)


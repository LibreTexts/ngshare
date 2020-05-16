# Unix file system APIs

import os, json, shutil, glob, traceback, base64, binascii

from app import request, app
from helper import (json_success, json_error, error_catcher, path_modifier,
					get_pathname, remove_pathname)

@app.route('/read')
@error_catcher
def read_file() :
	'''
		Read the content of a file
		Request
			pathname: Linux-style path and name of file
		Response
			content: base64 encoded content of file
	'''
	pathname = get_pathname()
	if not os.path.exists(pathname) :
		return json_error('File %s does not exist' % repr(pathname))
	try :
		f = open(pathname, 'rb')
		content = f.read()
		f.close()
	except PermissionError :
		return json_error('Permission Denied')
	except Exception :
		return json_error('Exception: %s' % repr(traceback.format_exc()))
	return json_success(content=base64.encodebytes(content).decode())

@app.route('/write')
@error_catcher
def write_file() :
	'''
		Write content to a file (overwrites original; creates new file)
		Request
			pathname: Linux-style path and name of file
			content: base64 encoded content
		Response
			length: Length written to file
			pathname: same as in request
	'''
	pathname = get_pathname()
	b64content = request.args.get('content')
	if b64content is None :
		return json_error('Please supply content using HTTP GET')
	try :
		content = base64.decodebytes(b64content.encode())
	except binascii.Error :
		return json_error('Content cannot be base64 decoded')
	directory = os.path.dirname(pathname)
	if not os.path.exists(directory) :
		return json_error('Directory %s does not exist' % repr(directory))
	try :
		f = open(pathname, 'wb')
		nbytes = f.write(content)
		f.close()
	except PermissionError :
		return json_error('Permission Denied')
	except Exception :
		return json_error('Exception: %s' % repr(traceback.format_exc()))
	return json_success('Written %d bytes to %s' % (nbytes, repr(pathname)),
						length=nbytes, pathname=pathname)

@app.route('/ls')
@error_catcher
def list_directory() :
	'''
		List a directory
		Request
			pathname: Linux-style path of directory
		Response
			content: json list of direcotry content
	'''
	pathname = get_pathname()
	if not os.path.exists(pathname) :
		return json_error('pathname does not exist')
	if not os.path.isdir(pathname) :
		return json_error('pathname is not directory')
	return json_success(content=os.listdir(pathname))

@app.route('/mkdir')
@error_catcher
def make_directory() :
	'''
		Make a directory
		Request
			pathname: Linux-style path of directory
			parent: (optional) 0 or 1, whether mkdir parent directories
		Response
			(none)
	'''
	pathname = get_pathname()
	parent = request.args.get('parent', '0') == '1'
	if os.path.exists(pathname) :
		return json_error('File exists')
	try :
		if parent :
			os.makedirs(pathname)
		else :
			os.mkdir(pathname)
	except Exception as e :
		return json_error(e.strerror)
	return json_success()

@app.route('/chmod')
@error_catcher
def change_mode() :
	'''
		Change mode of file or directory
		Request
			pathname: Linux-style path of file or directory
			mode: file mode in integer
		Response
			(none)
	'''
	pathname = get_pathname()
	parent = request.args.get('parent', '0') == '1'
	if not os.path.exists(pathname) :
		return json_error('pathname does not exist')
	try :
		mode = int(request.args.get('mode'))
	except ValueError :
		return json_error('Please supply mode in integer using HTTP GET')
	try :
		os.chmod(pathname, mode)
	except Exception as e :
		return json_error(e.strerror)
	return json_success()

@app.route('/stat')
@error_catcher
def status() :
	'''
		Display file status (permission, user, etc), wrapper for os.stat
		Request
			pathname: Linux-style path of file or directory
		Response
			mode: file mode in integer
			uid: user id in integer
			gid: group id in integer
			size: size in integer
			atime: access time in float
			mtime: modify time in float
			ctime: change time in float
	'''
	pathname = get_pathname()
	parent = request.args.get('parent', '0') == '1'
	if not os.path.exists(pathname) :
		return json_error('pathname does not exist')
	try :
		stat = os.stat(pathname)
	except Exception as e :
		return json_error(e.strerror)
	return json_success(mode=stat.st_mode,
						uid=stat.st_uid,
						gid=stat.st_gid,
						size=stat.st_size,
						atime=stat.st_atime,
						mtime=stat.st_mtime,
						ctime=stat.st_ctime)

@app.route('/glob')
@error_catcher
def globbing() :
	'''
		Return a list of paths matching a pathname pattern
		Request
			pathname: A pattern that is passed into glob.glob
		Response
			content: json list of direcotry content
	'''
	pathname = get_pathname(escape=glob.escape)
	return json_success(content=glob.glob(pathname))

@app.route('/walk')
@error_catcher
def os_walk() :
	'''
		Return a list of paths matching a pathname pattern
		Request
			pathname: A Linux-style path of file or directory
		Response
			content: json list of os.walk content
	'''
	# Maybe not safe when FS_PREFIX != '/'
	pathname = get_pathname()
	ans = []
	for p, d, f in os.walk(pathname):
		ans.append((remove_pathname(p), d, f))
	return json_success(content=ans)

@app.route('/exists')
@error_catcher
def os_path_exists() :
	'''
		Return whether a path is a directory
		Request
			pathname: A Linux-style path of file or directory
		Response
			exists: true or false indicating result
	'''
	pathname = get_pathname()
	return json_success(exists=os.path.exists(pathname))

@app.route('/isdir')
@error_catcher
def is_dir() :
	'''
		Return whether a path is a directory
		Request
			pathname: A Linux-style path of file or directory
		Response
			isdir: true or false indicating result
	'''
	pathname = get_pathname()
	return json_success(isdir=os.path.isdir(pathname))

@app.route('/isfile')
@error_catcher
def is_file() :
	'''
		Return whether a path is a directory
		Request
			pathname: A Linux-style path of file or directory
		Response
			isfile: true or false indicating result
	'''
	pathname = get_pathname()
	return json_success(isfile=os.path.isfile(pathname))

@app.route('/islink')
@error_catcher
def is_link() :
	'''
		Return whether a path is a directory
		Request
			pathname: A Linux-style path of file or directory
		Response
			islink: true or false indicating result
	'''
	pathname = get_pathname()
	return json_success(islink=os.path.islink(pathname))

@app.route('/ismount')
@error_catcher
def is_mount() :
	'''
		Return whether a path is a directory
		Request
			pathname: A Linux-style path of file or directory
		Response
			ismount: true or false indicating result
	'''
	pathname = get_pathname()
	return json_success(ismount=os.path.ismount(pathname))

@app.route('/copy')
@error_catcher
def copy_file() :
	'''
		Copy a file
		Request
			src: A Linux-style path of file or directory
			dst: A Linux-style path of file or directory
		Response
			(none)
	'''
	src = get_pathname('src')
	dst = get_pathname('dst')
	try :
		shutil.copy(src, dst)
	except PermissionError :
		return json_error('Permission Denied')
	except Exception :
		return json_error('Exception: %s' % repr(traceback.format_exc()))
	return json_success()

@app.route('/copytree')
@error_catcher
def copy_tree() :
	'''
		Copy a tree using shutil.copytree
		Call convention: (src, dst, ignore=shutil.ignore_patterns(*ignore))
		Request
			src: A Linux-style path of file or directory
			dst: A Linux-style path of file or directory
			ignore: list of json strings, passed to ignore_patterns(); optional
		Response
			(none)
	'''
	src = get_pathname('src')
	dst = get_pathname('dst')
	ignore = request.args.get('ignore', None)
	try :
		print(repr(ignore))
		if ignore is not None :
			ignore = shutil.ignore_patterns(*json.loads(ignore))
		shutil.copytree(src, dst, ignore=ignore)
	except PermissionError :
		return json_error('Permission Denied')
	except FileExistsError :
		return json_error('File exists')
	except FileNotFoundError :
		return json_error('No such file or directory')
	except Exception :
		return json_error('Exception: %s' % repr(traceback.format_exc()))
	return json_success()

@app.route('/rmtree')
@error_catcher
def remove_tree() :
	'''
		Copy a tree using shutil.copytree
		Call convention: (src, dst, ignore=shutil.ignore_patterns(*ignore))
		Request
			pathname: A Linux-style path of file or directory
		Response
			(none)
	'''
	pathname = get_pathname('pathname')
	try :
		shutil.rmtree(pathname)
	except PermissionError :
		return json_error('Permission Denied')
	except FileNotFoundError :
		return json_error('No such file or directory')
	except Exception :
		return json_error('Exception: %s' % repr(traceback.format_exc()))
	return json_success()


Deployment
==========

This project uses Travis CI to automatically upload packages to PyPI.

The ``stable`` branch will be used for PyPI deployment. When a new version of ``ngshare`` is ready, submit a pull request to merge from ``master`` to ``stable``, and increase the version number in ``ngshare/version.py`` (otherwise deployment will fail because of name conflict on PyPI).

``.travis.yml`` specifies that each build on ``stable`` branch with Python version 3.8 will trigger a deployment. 

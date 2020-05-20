Deployment
==========

This project uses Travis CI to automatically upload packages to PyPI.

``.travis.yml`` specifies that each build on ``master`` branch with Python version 3.8 will trigger a deployment. At that time version number need to be increased, or build will fail because of name conflict on PyPI.


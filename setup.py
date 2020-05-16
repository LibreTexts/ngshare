import setuptools
import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ngshare",
    version=get_version('ngshare/version.py'),
    author="Team KALE",
    author_email="ercli@ucdavis.edu",
    description="nbgrader sharing service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lxylxy123456/ngshare",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
    install_requires=[
        'SQLAlchemy>=1.3.12',
        'alembic>=1.3.2',
        'tornado>=6.0.3',
        'jupyterhub>=1.1.0',
    ],
)

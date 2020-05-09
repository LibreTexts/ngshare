"""Database utilities for nbgrader"""
# Based on jupyterhub.dbutil
# Based on nbgrader.dbutil

import os
import sys
import tempfile
import shutil
import _io

from contextlib import contextmanager
from subprocess import check_call
from typing import Iterator, Tuple

_here = os.path.abspath(os.path.dirname(__file__))

ALEMBIC_INI_TEMPLATE_PATH = os.path.join(_here, 'alembic.ini')
ALEMBIC_DIR = os.path.join(_here, 'alembic')

DEFAULT_DB = 'sqlite:////tmp/ngshare.db'

def write_alembic_ini(file_obj: _io.BufferedRandom, db_url: str = DEFAULT_DB) -> None:
    """Write a complete alembic.ini from our template.
    Parameters
    ----------
    alembic_ini: str
        path to the alembic.ini file that should be written.
    db_url: str
        The SQLAlchemy database url, e.g. `sqlite:///ngshare.db`.
    """
    with open(ALEMBIC_INI_TEMPLATE_PATH) as f:
        alembic_ini_tpl = f.read()

    file_obj.write(
        alembic_ini_tpl.format(
            alembic_dir=ALEMBIC_DIR,
            db_url=db_url,
        ).encode()
    )


@contextmanager
def _temp_alembic_ini(db_url: str) -> Iterator[Tuple[str, int]]:
    """Context manager for temporary JupyterHub alembic directory
    Temporarily write an alembic.ini file for use with alembic migration scripts.
    Context manager yields alembic.ini path.
    Parameters
    ----------
    db_url:
        The SQLAlchemy database url, e.g. `sqlite:///gradebook.db`.
    Returns
    -------
    alembic_ini:
        The path to the temporary alembic.ini that we have created.
        This file will be cleaned up on exit from the context manager.
    """
    tf = tempfile.TemporaryFile()
    try:
        write_alembic_ini(tf, db_url)
        tf.seek(0, 0)
        fd = tf.fileno()
        yield '/dev/fd/%d' % fd, fd
    finally:
        tf.close()


def upgrade(db_url, revision='head'):
    """Upgrade the given database to revision.
    db_url: str
        The SQLAlchemy database url, e.g. `sqlite:///ngshare.db`.
    revision: str [default: head]
        The alembic revision to upgrade to.
    """
    with _temp_alembic_ini(db_url) as (alembic_ini, fd):
        check_call(
            ['alembic', '-c', alembic_ini, 'upgrade', revision],
            pass_fds=(fd,)
        )


def _alembic(*args):
    """Run an alembic command with a temporary alembic.ini"""
    with _temp_alembic_ini(DEFAULT_DB) as (alembic_ini, fd):
        check_call(
            ['alembic', '-c', alembic_ini] + list(args),
            pass_fds=(fd,)
        )


if __name__ == '__main__':
    _alembic(*sys.argv[1:])

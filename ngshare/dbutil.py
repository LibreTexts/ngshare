"""Database utilities for nbgrader"""
# Based on jupyterhub.dbutil
# Based on nbgrader.dbutil

import os
import sys

import alembic
import alembic.command
import alembic.config

_here = os.path.abspath(os.path.dirname(__file__))

ALEMBIC_INI_TEMPLATE_PATH = os.path.join(_here, 'alembic.ini')
ALEMBIC_DIR = os.path.join(_here, 'alembic')

DEFAULT_DB = 'sqlite:////tmp/ngshare.db'


def get_alembic_config(db_url: str = DEFAULT_DB) -> alembic.config.Config:
    """Generate the alembic configuration from the template and populate fields.
    db_url: str [default: 'sqlite:////tmp/ngshare.db']
        The database url used to populate sqlalchemy.url, e.g. `sqlite:///ngshare.db`.
    """

    config = alembic.config.Config(ALEMBIC_INI_TEMPLATE_PATH)
    config.set_main_option("script_location", ALEMBIC_DIR)
    config.set_main_option("sqlalchemy.url", db_url)
    return config


def upgrade(db_url: str = DEFAULT_DB, revision='head'):
    """Upgrade the given database to revision.
    db_url: str [default: 'sqlite:////tmp/ngshare.db']
        The SQLAlchemy database url, e.g. `sqlite:///ngshare.db`.
    revision: str [default: head]
        The alembic revision to upgrade to.
    """
    alembic.command.upgrade(get_alembic_config(db_url), revision)


def main(args: list, db_url: str = DEFAULT_DB):
    """Run an alembic command with the right config"""
    cl = alembic.config.CommandLine()
    options = cl.parser.parse_args(args)
    if not hasattr(options, "cmd"):
        cl.parser.error("too few arguments")
    cl.run_cmd(get_alembic_config(db_url), options)


if __name__ == '__main__':  # pragma: no cover
    main(sys.argv[1:])

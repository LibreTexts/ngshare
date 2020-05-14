try:
    from .version import __version__
except ImportError:  # pragma: no cover
    from version import __version__

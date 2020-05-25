try:
    from .version import __version__
    from . import ngshare
except ImportError:  # pragma: no cover
    from version import __version__
    import ngshare

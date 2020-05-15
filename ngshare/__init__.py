try:
    from .version import __version__
    from . import ngshare, vngshare
except ImportError:
    from version import __version__
    import ngshare, vngshare

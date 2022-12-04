Change Log
==========

ngshare
-------

0.6.0
^^^^^

- Compatibility with JupyterHub 3.0
- Updated authentication to use OAuth (Thanks `joernahlers <https://github.com/joernahlers>`_ for `PR #151 <https://github.com/LibreTexts/ngshare/pull/151>`_!)
- Migrated CI/CD to GitHub Actions

0.5.3
^^^^^

- Fix not having a `deployment.strategy` causing helm chart rendering to fail.

0.5.2
^^^^^
- Update helm chart to allow configuring the `accessMode` of ngshare's PVC via `pvc.accessModes`. The PVC will be mounted `ReadWriteMany` by default unless you override this value. (Thanks `pcfens <https://github.com/pcfens>`_) for the `PR #120 <https://github.com/LibreTexts/ngshare/pull/120>`_!)
- Update helm chart to allow `initContainers` to be added, via `deployment.initContainers`. This is an array of `initContainers`, such as expected in Kubernetes, and such as implemented in Z2JH itself.
- Update helm chart to allow `strategy` to be specified, via `deployment.strategy`. This is an object passed to the Deployment's `strategy`, as specified in the Kubernetes documentation at https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy.

0.5.1
^^^^^

- Update helm chart with clearer installation instructions
- Misc. documentation updates to help with installation
- Transfer repository ownership to LibreTexts, change all GitHub links and tokens related to Travis, PyPI, etc
- Test Travis autopublishing a stable release

0.5.0
^^^^^
Initial release intended for the public.


ngshare_exchange
----------------

0.5.3
^^^^^

- Fixed dependencies
- Migrated CI/CD to GitHub Actions

0.5.2
^^^^^

- Bug fixes
- Fixed dependencies

0.5.1
^^^^^

- Drastically increase test coverage
- Removed some dead code
- Several important bugfixes and typo fixes in the exchange classes and course management tool
- Transfer repository ownership to LibreTexts, change all GitHub links and tokens related to Travis, PyPI, etc
- Test Travis autopublishing a stable release

0.5.0
^^^^^
Initial release intended for the public.

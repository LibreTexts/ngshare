Change Log
==========

0.5.3
-----

ngshare:

- Fix not having a `deployment.strategy` causing helm chart rendering to fail.

0.5.2
-----

ngshare:

- Update helm chart to allow configuring the `accessMode` of ngshare's PVC via `pvc.accessModes`. The PVC will be mounted `ReadWriteMany` by default unless you override this value. (Thanks [pcfens](https://github.com/pcfens) for the [PR](https://github.com/LibreTexts/ngshare/pull/120)!)
- Update helm chart to allow `initContainers` to be added, via `deployment.initContainers`. This is an array of `initContainers`, such as expected in Kubernetes, and such as implemented in Z2JH itself.
- Update helm chart to allow `strategy` to be specified, via `deployment.strategy`. This is an object passed to the Deployment's `strategy`, as specified in the Kubernetes documentation at https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy.

0.5.1
-----

ngshare:

- Update helm chart with clearer installation instructions
- Misc. documentation updates to help with installation
- Transfer repository ownership to LibreTexts, change all GitHub links and tokens related to Travis, PyPI, etc
- Test Travis autopublishing a stable release

ngshare_exchange:

- Drastically increase test coverage
- Removed some dead code
- Several important bugfixes and typo fixes in the exchange classes and course management tool
- Transfer repository ownership to LibreTexts, change all GitHub links and tokens related to Travis, PyPI, etc
- Test Travis autopublishing a stable release

0.5.0
-----
Initial release intended for the public.


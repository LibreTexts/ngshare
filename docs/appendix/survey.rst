Technology Survey
=================

The Problem
-----------

nbgrader can be used in JupyterHub for creating and grading assignments, but there are issues when JupyterHub is deployed as a Kubernetes cluster. nbgrader distributes and collects assignments via a shared directory between instructors and students called the exchange directory. nbgrader does not work on a Kubernetes setup because there isn't a shared filesystem in which to place the exchange directory. 

.. image:: ../assets/architecture5a.svg
    :alt: Original System Architecture Diagram
    :align: center

Alternative Solutions
---------------------

We brainstormed a few possible solutions before starting the ngshare project:

hubshare
^^^^^^^^

`hubshare <https://github.com/jupyterhub/hubshare>`_ is a directory sharing
service for JupyterHub.

Pros
""""

* Universal solution which can be integrated with nbgrader.

* Considered for a similar service desired by the primary nbgrader developer
  (see
  `jupyter/nbgrader#659 <https://github.com/jupyter/nbgrader/issues/659>`_).

Cons
""""

* Lots of work to implement HubShare.

* The nbgrader exchange needs to be reworked.

* Too generic, as it does not have permission control specific to courses and
  assignments (see
  `this comment <https://github.com/jupyter/nbgrader/issues/659#issuecomment-431762792>`_).

NFS
^^^

Another solution is to let every container access a shared file system
through NFS (Network File System).

Pros
""""

* Simple and doable.

* Requires minimal changes and additions to the Jupyter project.

Cons
""""

* Not a universal solution. NFS setups will vary across deployments.

Kubernetes Persistent Volume Claim
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Kubernetes Persistent Volume Claim
<https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims>`_
allows containers to request shared file systems.

Pros
""""

* More universal than the NFS solution.

* Requires minimal changes and additions to the Jupyter project.

Cons
""""

* Difficult to work around limitations regarding multiple writers per
  volume. Need to find a way to have correct permissions for students and
  instructors.

* Does not work with `some volume plugins <https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes>`_.

We think the best of these solutions is hubshare, but it is too general. We decided to create our own solution, which is a service similar to hubshare but more specialized for nbgrader. We call it ngshare, short for **n**\ b\ **g**\ rader **share**.

ngshare
-------

ngshare implements a set of :doc:`REST APIs </api/index>` designed
for the nbgrader exchange mechanism.

Pros
^^^^

* Universal solution which can be integrated with nbgrader.

* **Full control over APIs in this project.**

Cons
^^^^

* Work needs to be done to implement ngshare.

* The nbgrader exchange needs to be reworked.

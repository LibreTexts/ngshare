Why ngshare?
============

We brainstormed a few possible solutions before starting the ngshare project:

* hubshare

  * `hubshare <https://github.com/jupyterhub/hubshare>`_ is a directory sharing
    service for JupyterHub. 

  * Pros

    * Universal solution that can be integrated with nbgrader.

    * Similar service desired by nbgrader developer 
      (see
      `jupyter/nbgrader#659 <https://github.com/jupyter/nbgrader/issues/659>`_)

  * Cons

    * Lots of work to implement HubShare. 

    * nbgrader exchange mechanism need to be reworked.

    * Too generic, does not have permission control specific to classes &
      assignment. (see
      `this comment <https://github.com/jupyter/nbgrader/issues/659#issuecomment-431762792>`_)

* NFS

  * Another solution is to let every container access a shared file system
    through NFS (Network File System).

  * Pros

    * Very doable. Does not "require" input from the Jupyter community.

  * Cons

    * Not a universal solution.

* Kubernetes Persistent Volume Claim

  * `Kubernetes Persistent Volume Claim
    <https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims>`_
    allows containers to request shared file systems.

  * Pros

    * More universal than the NFS solution. Does not "require" input from
      the Jupyter community.

  * Cons

    * Difficult to work around limitations regarding multiple writers per
      volume. Need to find a way to have correct permissions for students and
      instructors.

The best solution we think is the first one, but the generic problem still need to be solved. So we decided to find a fourth solution, which is creating a service similar to hubshare but more specialized for nbgrader.

* ngshare

  * ngshare implements a set of :doc:`REST APIs </api/index>` designed
    for nbgrader exchange mechanism.

  * Pros

    * Universal solution that can be integrated with nbgrader.

    * **Fully controlled APIs by this project.**

  * Cons

    * Work needs to be done to implement ngshare.

    * nbgrader exchange mechanism needs to be reworked. 


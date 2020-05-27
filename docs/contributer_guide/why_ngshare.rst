Why ngshare?
============

The Problem
-----------

nbgrader can be used in JupyterHub for creating and grading assignments, but there are issues when JupyterHub is deployed as a Kubernetes cluster. nbgrader distributes and collects assignments via a shared directory between instructors and students called the exchange directory. nbgrader does not work on a Kubernetes setup because there isn't a shared filesystem in which to place the exchange directory. 

.. tikz::

	\newcommand{\DrawRect}[3]{
		\filldraw[fill=lightblue, draw=black]
			(#1 - 2, #2 - 0.5) rectangle ++(4, 1);
			\draw (#1, #2) node[align=center] {#3};
	}
	\newcommand{\DrawLine}[2]{
		\draw[#1, line width=0.5mm, color=#2]
	}
	\definecolor{lightblue}{HTML}{cfe2f3}
	\def\ux{0}		\def\uy{4}
	\def\px{0}		\def\py{1.5}
	\def\hx{0}		\def\hy{-0.5}
	\def\ax{-2.5}	\def\ay{-3}
	\def\bx{2.5}	\def\by{-3}
	\def\nx{7.5}	\def\ny{-0.5}
	\filldraw[fill=lightblue!30!white, draw=black] (6, -4.5) rectangle (-6, 3)
		node[below right] {Kubenetes Cluster};
	\filldraw[fill=lightblue!50!white, draw=black] (5, -4) rectangle (-5, 2)
		node[below right] {JupyterHub};
	\DrawRect{\ux}{\uy}{Users}
	\DrawRect{\px}{\py}{Proxy \\ (k8s Pod \& Service)}
	\DrawRect{\hx}{\hy}{Hub \\ (k8s Pod \& Service)}
	\DrawRect{\ax}{\ay}{Jupyter Notebook\\nbgrader (k8s Pod)}
	\DrawRect{\bx}{\by}{Jupyter Notebook\\nbgrader (k8s Pod)}

	\DrawLine{->}{black} (\ux, \uy-0.5) -- (\px, \py+0.5);

	\DrawLine{->}{blue} (\px-2, \py-0.5) to[bend right=10] (\ax-0.5, \ay+0.5);
	\DrawLine{->}{blue} (\px+2, \py-0.5) to[bend left=10] (\bx+0.5, \by+0.5);
	\DrawLine{->}{blue} (\px, \py-0.5) -- (\hx, \hy+0.5)
					node[pos=0.5, right]{Proxying};

	\draw[color=orange] (0, -1.75) node{Spawn};
	\DrawLine{->}{orange} (\hx-1, \hy-0.5) to[bend right=10] (\ax+1, \ay+0.5);
	\DrawLine{->}{orange} (\hx+1, \hy-0.5) to[bend left=10] (\bx-1, \by+0.5);

	\DrawLine{<->}{brown} (\ax+2, \ay) to (\bx-2, \by);
	\draw[line width=1mm, color=red] (-0.2, \ay-0.2) to (0.2, \ay+0.2);
	\draw[line width=1mm, color=red] (-0.2, \ay+0.2) to (0.2, \ay-0.2);

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

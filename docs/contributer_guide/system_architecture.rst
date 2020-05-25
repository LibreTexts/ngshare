System Architecture Overview
============================

``ngshare`` is intended to run as a Kubernetes pod and service outside JupyterHub. In a Kubernetes setup, ngshare is proxied by JupyterHub's proxy service and can be accessed from any JupyterHub user pod. It uses the Hub for authentication.

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
	\filldraw[fill=lightblue!30!white, draw=black] (10, -4.5) rectangle (-6, 3)
		node[below right] {Kubenetes Cluster};
	\filldraw[fill=lightblue!50!white, draw=black] (5, -4) rectangle (-5, 2)
		node[below right] {JupyterHub};
	\DrawRect{\ux}{\uy}{Users}
	\DrawRect{\px}{\py}{Proxy \\ (k8s Pod \& Service)}
	\DrawRect{\hx}{\hy}{Hub \\ (k8s Pod \& Service)}
	\DrawRect{\ax}{\ay}{Jupyter Notebook\\nbgrader (k8s Pod)}
	\DrawRect{\bx}{\by}{Jupyter Notebook\\nbgrader (k8s Pod)}
	\DrawRect{\nx}{\ny}{ngshare Service \\ (k8s Pod \& Service)}

	\DrawLine{->}{black} (\ux, \uy-0.5) -- (\px, \py+0.5);

	\DrawLine{->}{blue} (\px-2, \py-0.5) to[bend right=10] (\ax-0.5, \ay+0.5);
	\DrawLine{->}{blue} (\px+2, \py-0.5) to[bend left=10] (\bx+0.5, \by+0.5);
	\DrawLine{->}{blue} (\px+2, \py) to[bend left=10] (\nx-1.5, \ny+0.5);
	\DrawLine{->}{blue} (\px, \py-0.5) -- (\hx, \hy+0.5)
					node[pos=0.5, right]{Proxying};

	\draw[color=orange] (0, -1.75) node{Spawn};
	\DrawLine{->}{orange} (\hx-1, \hy-0.5) to[bend right=10] (\ax+1, \ay+0.5);
	\DrawLine{->}{orange} (\hx+1, \hy-0.5) to[bend left=10] (\bx-1, \by+0.5);

	\DrawLine{<->}{brown} (\ax+2, \ay-0.5) to[bend right=40] (\nx+1, \ny-0.5);
	\DrawLine{<->}{brown} (\bx+2, \by+0.5) -- (\nx-1, \ny-0.5)
							node[pos=0.5, below right]{Exchange};

	\DrawLine{->}{purple} (\nx-2, \ny) -- (\hx+2, \hy)
							node[pos=0.5, above]{Authenticate};

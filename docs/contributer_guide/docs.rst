Documentation
=============

This project uses Sphinx to generate documentation for Read the Docs

.. code:: bash

    pip3 install sphinx sphinxcontrib-tikz
    cd docs
    make html

.. tikz:: A beautiful TikZ drawing which works in readthedocs.org.

   \draw[thick,rounded corners=8pt]
   (0,0)--(0,2)--(1,3.25)--(2,2)--(2,0)--(0,2)--(2,2)--(0,0)--(2,0);
   \definecolor{lightblue}{HTML}{cfe2f3}
   \def\ux{0}
   \filldraw[fill=lightblue!30!white, draw=black] (10, -4.5) rectangle (-6, 3);


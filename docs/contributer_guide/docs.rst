Documentation
=============

This project uses Sphinx to generate documentation for Read the Docs. To
install make dependencies and generate the HTML version of the documentation,
run the following.

.. code:: bash

    pip3 install sphinx sphinxcontrib-tikz sphinx_rtd_theme
    cd docs
    make html

You may need to install other LaTeX packages to make TikZ images work properly. For example, on Arch Linux, you need to use ``pacman -S texlive-core texlive-latexextra texlive-pictures``.

See `https://sphinxcontrib-tikz.readthedocs.io/en/latest/#prerequisites-and-configuration <https://sphinxcontrib-tikz.readthedocs.io/en/latest/#prerequisites-and-configuration>`_ for details.

Documentation Formatting
------------------------

For titles, use title case (e.g. "Documentation Formatting"), but do not capitalize things like "ngshare", "a", "the", etc.


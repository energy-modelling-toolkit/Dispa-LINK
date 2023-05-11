################
 Installation
################


Getting Python
==============

If it's your first time with Python, we recommend using either `conda
<https://docs.conda.io/en/latest/miniconda.html>`_, `mamba
<https://github.com/mamba-org/mamba>`_ or `pip
<https://pip.pypa.io/en/stable/>`_ as easy-to-use package managers.
They are available for Windows, Mac OS X, and GNU/Linux.

.. tip::
    It's always helpful to use dedicated `conda/mamba environments <https://mamba.readthedocs.io/en/latest/user_guide/mamba.html>`_ or `virtual environments
    <https://pypi.python.org/pypi/virtualenv>`_.


Installing Dispa-LINK with conda
================================

If you're using conda, you can install Dispa-LINK with the following command::

    conda install -c conda-forge dispa_link

In all of the above commands, you can replace ``conda`` with ``mamba`` if you use this alternative.


Installing Dispa-LINK with pip
==============================

If you have the Python package installer ``pip``, run the following command::

    pip install dispa_link

If you're feeling adventurous, you can also install the latest master branch from GitHub with::

    pip install git+https://github.com/energy-modelling-toolkit/Dispa-LINK.git


Conservative installation
=========================

If you're very conservative and don't like package managers, you can simply download the code from the
`Dispa-LINK github repository
<https://github.com/energy-modelling-toolkit/Dispa-LINK/>`_, and add the directory of Dispa-LINK to your Python path with, for example::

    import sys

    sys.path.append("path/to/Dispa-LINK")

    import dispa_link


Upgrading Dispa-LINK
====================

We recommend always keeping your Dispa-LINK installation up-to-date, as bugs get fixed and new features are added. Dispa-LINK is also only tested with the latest stable versions of all the dependent packages for the respective Python versions.

To upgrade Dispa-LINK with pip, do the following at the command line::

    pip install -U dispa_link

To upgrade Dispa-LINK with conda, use the following command::

    conda update dispa_link

.. note::
    Don't forget to read the :doc:`../HelpAndReferences/release_notes` regarding API changes
    that might require you to update your code.
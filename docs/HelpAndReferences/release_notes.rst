#######################
Release Notes
#######################

Upcoming Release
================
.. warning:: The features listed below are not released yet, but will be part of the upcoming releases! To use some of the features already you have to install the ``develop`` branch, e.g. ``pip install git+https://github.com/energy-modelling-toolkit/Dispa-LINK/tree/develop``.

* linking with the JRC-EU-TIMES ProRES scenario
* linking with the SDDP Bolivia
* A more advanced plotting of soft-linking variables including the convergence rate
* Github Action to automatically deploy

Dispa-LINK 0.1.0 (15th May 2023)
=================================

* First official release of the Dispa-LINK library

Release process
===============

* Update ``doc/release_notes.rst``
* Update version in ``setup.py``, ``doc/conf.py``, ``dispa_link/__init__.py``
* ``git commit`` and put release notes in commit message
* ``git tag v0.x.0``
* ``git push`` and  ``git push --tags``

..
    * The upload to `PyPI <https://pypi.org/>`_ is automated in the Github Action ``deploy.yml``.
      To upload manually, run ``python setup.py sdist``,
      then ``twine check dist/dispa_link-0.x.0.tar.gz`` and
      ``twine upload dist/dispa_link-0.x.0.tar.gz``
    * To update to conda-forge, check the pull request generated at the `feedstock repository
      <https://github.com/conda-forge/dispa_link-feedstock>`_.
    * Making a `GitHub release <https://github.com/energy-modelling-toolkit/Dispa-LINK/tree/releases>`_
      will trigger `zenodo <https://zenodo.org/>`_ to archive the release
      with its own DOI.

* Inform the Dispa-LINK mailing list.

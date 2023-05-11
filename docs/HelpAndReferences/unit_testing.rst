########################
Unit Testing
########################


Unit testing is performed with ``pytest`` that can be installed via

.. code::

    pip install pytest

The tests can be found in ``dispa_link/test/`` and can be run from there via

.. code::

    pytest

Or to run individual tests:

.. code::

    pytest test_xxx.py

Unit testing of new GitHub commits is automated with Github Actions.
Pyseries 1.1.1
---------------

TODO: write usage...

What's next
===========

#. Accept a list of ignored hosters (by URL)
#. Accept a list of prefered hosters (by URL) - these links are prefered
#. Prefere links that have a good quality declared (eg. HD or 10/10 video)

Setup development environment
===============================

Please note that this works only on linux!

1. Ensure you have `make` and `docker` installed on your system
2. Cd into the project's root directory
3. Run the following commands:

  .. code:: bash

    make buildimage # Builds the docker image
    make dev # Launches our development environment


  You will find yourself within a docker container (bash). Have fun!

Running the tests
+++++++++++++++++

Run the tests with the `nosetests` command line utility.

.. code:: bash

    $ nosetests
    ........
    Name                         Stmts   Miss  Cover   Missing
    ----------------------------------------------------------
    pyseries                       153     56    63%   28, 34, ...
    pyseries.special_treatment       8      1    88%   20
    ----------------------------------------------------------
    TOTAL                          161     57    65%
    ----------------------------------------------------------------------
    Ran 8 tests in 5.254s

    OK


For more details checkout the (`nose documentation <https://nose.readthedocs.org/en/latest/>`__)

If you want to test the created wheel distribution, create the wheel in the dev environment first. After that,
exit the dev container and run `make integration` in the project root.

This will fire up a docker container based on the official python image with the workspace mounted
read-only in the current working directory. You can no install the wheel with `pip`:

.. code:: bash

    $ pip install dist/pyseries-X.X.X-py3-none-any.whl
        Processing ./dist/pyseries-X.X.X-py3-none-any.whl
    ....


Releasing
=========

Note that your *host* system must declare the git config attributes `user.name` and `user.email`.

1. Check if the current version is OK (in the file `setup.cfg` the property `bumpversion:current_version`)
2. You can manually override the version using `bumpversion` available in the dev container

  .. code:: bash

    bumpversion --allow-dirty --no-tag --message "Next version will be {new_version}" --new-version z.y.x any

3. Next, leave the dev container (if not yet done) and run the command

.. code:: bash

  make release

4. If you are realy ready to go - press `enter`. If not, abort with `Ctrl+C`

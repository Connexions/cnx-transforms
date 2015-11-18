CNX Transforms
==============

Functions used to transform CNX content export formats.
This package is a set of functions that create very specific output.

The design of this package's functions is suppose to adhere to
a common interface. All functions accept an ``cnx-epub`` compatible
EPUB file and output one or more artifacts.


Getting Started
---------------

Install using one of the following methods (run within the project root)::

    python setup.py install

Or::

    pip install .

Testing
-------

.. image:: https://travis-ci.org/Connexions/cnx-transforms.svg
   :target: https://travis-ci.org/Connexions/cnx-transforms

::

    python setup.py test


Developer Notes
---------------

This package is built on the [Celery](celeryproject.org) message queuing framework with
the assumption that it will be used by ``cnx-publishing-builds``. It is kept as a separate
package so that the web framework and other dependencies in ``cnx-publishing-builds``
will not be required when setting up this project on a separate machine
from the machine running the web application.

When developing new transform functions, keep in mind that they should be kept
specific and minimal to the task at hand. For example, do not try to build
a PDF creation task that also builds PDF previews. Why? Because you should
be able to scale (limit or prioritize) the tasks. That is to say, build
a separate function for each case.

Manually testing a task
~~~~~~~~~~~~~~~~~~~~~~~

This package contains a module named ``main``, which houses the initialized
Celery application. It can additionally be used to run a single task
from the commandline. For example::

    python -m cnxtransforms.main --broker amqp://guest@localhost \
      cnxtransforms.tasks:make_pdf ../my-book.epub

License
-------

This software is subject to the provisions of the GNU Affero General
Public License Version 3.0 (AGPL). See license.txt for
details. Copyright (c) 2013 Rice University

# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2014, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import io
import argparse
from importlib import import_module

from celery import Celery


__all__ = ('app')


app = Celery('tasks')


def _import_dotted_path(path):
    """Imports the function at the given dotted ``path``.
    For example::

        cnxtransforms.tasks:make_pdf

    """
    module_path, function = path.split(':')
    package_path = module_path.split('.')
    package = '.'.join(package_path[:-1])
    if not package:
        module = package_path[0]
    else:
        # Relative path to module
        module = '.' + package_path[-1]
    m = import_module(module, package)
    return getattr(m, function)


def main(argv=None):
    global app
    parser = argparse.ArgumentParser("Celery example process")
    parser.add_argument('-b', '--broker', default='amqp://guest@localhost',
                        help="address of the broker")
    parser.add_argument('task_path',
                        help="dotted path to a function (e.g. os.path:join)")
    parser.add_argument('epub', type=argparse.FileType('r'),
                        help="location of the epub file")
    args = parser.parse_args(argv)
    kwargs = {
        'BROKER_URL': args.broker,
        }
    app.conf.update(**kwargs)
    task = _import_dotted_path(args.task_path)
    epub = io.BytesIO(args.epub.read())
    task.delay(epub)
    return


if __name__ == '__main__':
    main()

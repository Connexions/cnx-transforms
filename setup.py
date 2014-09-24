# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages


IS_PY3 = sys.version_info > (3,)

install_requires = (
    'celery',
    )
tests_require = [
    ]
extras_require = {
    'test': tests_require,
    }
description = """Functions used to convert CNX content to export formats."""

if not IS_PY3:
    tests_require.append('mock')

setup(
    name='cnx-transforms',
    version='0.1',
    author='Connexions team',
    author_email='info@cnx.org',
    url="https://github.com/connexions/cnx-transforms",
    license='AGPL, See also LICENSE.txt',
    description=description,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    test_suite='cnxtransforms.tests',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'cnxtransforms': [],
        },
    entry_points="""\
    """,
    )

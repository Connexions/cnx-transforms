# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""Transformations commandline interface (CLI)"""
import sys
import argparse

import cnxtransforms


def init_parser(parser=None):
    """Initialize the commandline argument parser"""
    if parser is None:
        parser = argparse.ArgumentParser(description=__doc__)
    # Source and destination are the only positional arguments and do
    #   not need to be passed in, because we read from stdin and write
    #   to stdout when these are not provided. This closely resembles
    #   the docutils commandline interfaces.
    parser.add_argument('source', nargs='?',
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        help="source file to convert")
    parser.add_argument('destination', nargs='?',
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help="destination file to write the output")
    return parser

def word2soffice(args=None, parser=None):
    parser = init_parser(parser)
    parser.add_argument('--server-address',
                        help="host and port to the headless *office")
    args = parser.parse_args(args)

    # And now the body of work...
    cnxtransforms.word_to_odt(args.source, output=args.destination)
    return 0

def soffice2cnxml(args=None, parser=None):
    """*office to CNXML
    Input an office document (e.g. docx, odt). The output will be a zip that
    contains the CNXML and any resources in the document.

    """
    parser = init_parser(parser)
    args = parser.parse_args(args)

    # And now the body of work...
    content = cnxtransforms.odt_to_cnxml(args.source)
    cnxtransforms.to_zipfile(content, output=args.destination)
    return 0

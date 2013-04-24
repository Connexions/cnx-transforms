# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""Logging facilities for this package. Handles logging
initialization with reasonable defaults.

The ``logger`` provided by this module should be used in library logging.

"""
import os
import sys
import logging
from logging.config import fileConfig as load_logging_configuration


__all__ = ('logger', 'make_logger',)
here = os.path.abspath(os.path.dirname(__file__))
PACKAGE_LOGGER_NAME = 'cnxtransforms'
LOGGING_CONFIG_LOCATIONS = (
    '/etc/cnx-transforms/logging.cfg',
    os.path.join(os.path.expanduser('~/.cnx-transforms'), 'logging.cfg'),
    os.path.join(here, 'default-logging.cfg'),
    )
logger = None


def make_logger(name=''):
    """Create a logger using the context or return the default logger."""
    return logging.getLogger(name)

def _init_default_logger():
    """Loads a set of sane defaults that we can use to provide a minimal
    amount of logging without direct interaction by the library or commandline
    user.

    """
    global logger
    if logger is not None:
        return
    is_configured = False
    cfg_used = None
    for config in LOGGING_CONFIG_LOCATIONS:
        if os.path.exists(config):
            cfg_used = config
            load_logging_configuration(config)
            is_configured = True
            break
    if not is_configured:
        raise RuntimeError("Missing a logging configuration file")

    logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    logger.debug("Initialized")
    logger.debug("Using logging configuration at '{}'.".format(cfg_used))

_init_default_logger()

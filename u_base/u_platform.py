#!/usr/bin/python
# -*- coding: utf-8 -*
# base platform function

import select
import platform

__all__ = [
    'is_linux',
    'is_windows',
    'is_mac'
]


def is_linux():
    """
    Check if you are running on Linux.
    :return: True or False
    """
    if platform.platform().startswith('Linux'):
        return True
    else:
        return False


def is_windows():
    """
    Check if you are running on Windows.
    :return: True or False
    """

    if platform.platform().startswith('Windows'):
        return True
    else:
        return False


def is_mac():
    """
    Check if you are running on mac os
    :return: True or False
    """
    if hasattr(select, 'kqueue'):
        return True
    else:
        return False

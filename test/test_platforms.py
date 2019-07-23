#!/usr/bin/python
# -*- coding: utf-8 -*
import u_base.u_platform as u_platform


def test_is_windows():
    assert u_platform.is_windows() is True


def test_is_mac():
    assert u_platform.is_mac() is False


def test_is_linux():
    assert u_platform.is_linux() is False

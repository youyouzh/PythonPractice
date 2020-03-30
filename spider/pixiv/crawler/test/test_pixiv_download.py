#!/usr/bin/env python
# -*- coding: utf-8 -*-

from u_base import u_unittest
from spider.pixiv.crawler.pixiv_download import get_10_20


def test_get_10_20():
    u_unittest.assert_eq(8, get_10_20(8)[0])
    u_unittest.assert_eq(10, get_10_20(18)[0])
    u_unittest.assert_eq(3000, get_10_20(3999)[0])

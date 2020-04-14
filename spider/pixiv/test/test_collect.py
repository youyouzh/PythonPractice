#!/usr/bin/env python
# -*- coding: utf-8 -*-

from u_base import u_unittest
from spider.pixiv.arrange.collect import *
from spider.pixiv.mysql.db import session, Illustration


def test_update_illust_tag():
    illust_id = 8681586
    file_path = r'..\crawler\result\collect\temp'
    update_illust_tag(file_path, 'gray')
    source_illust = session.query(Illustration).get(illust_id)
    u_unittest.assert_eq('gray', source_illust.tag)

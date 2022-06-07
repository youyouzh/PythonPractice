#!/usr/bin/env python
# -*- coding: utf-8 -*-

from u_base import u_unittest
from spider.pixiv.arrange.arrange import *
from spider.pixiv.mysql.db import session, Illustration


def test_get_illust_id():
    file = r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result\ignore\small\56765988_p0-5' \
           r'年後神楽-沖田総悟-沖神-神楽-神沖-銀魂-銀魂10000users入り.jpg'
    illust_id = get_illust_id(file)
    u_unittest.assert_eq(56765988, illust_id)


def test_check_user_id():
    target_directory = r'..\crawler\result\collect\4754550-可爱画风-check\4752417'
    move_user_illusts(target_directory)

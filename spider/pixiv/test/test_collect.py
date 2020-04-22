#!/usr/bin/env python
# -*- coding: utf-8 -*-

from u_base import u_unittest
from spider.pixiv.arrange.collect import *
from spider.pixiv.mysql.db import session, Illustration


def test_update_illust_tag():
    file_path = r'..\crawler\result\collect\74184-check'
    update_illust_tag(file_path, 'ignore')


def test_collect_illusts():
    user_id = 10292
    collect_illusts(str(user_id), is_special_illust_ids, 1000, user_id=user_id)


def test_check_user_id():
    target_directory = r'..\crawler\result\collect\4754550-可爱画风-check\4752417'
    check_user_id(target_directory)

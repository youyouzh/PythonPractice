#!/usr/bin/python
# -*- coding: utf-8 -*
import os
import re
from urllib.parse import quote, unquote

import u_base.u_file as u_file
import u_base.u_log as u_log
import u_base.u_unittest as u_unittest


def test_cache_json():
    json_data = {'a': 1, 'b': 2}
    cache_file = u_file.cache_json(json_data)
    u_unittest.assert_true(os.path.isfile(cache_file))


def test_read_write_file():
    content = '--something--'
    file_path = r'cache\test.dat'
    file_path = os.path.abspath(file_path)
    u_file.write_content(file_path, content)
    u_unittest.assert_eq(content, u_file.read_content(file_path))


def test_get_file_name_from_url():
    url = 'https://files.yande.in/image/yande.re%20485154%20bra%20breasts%20nipples%20nurse%20thighhighs.png'
    u_unittest.assert_eq('yande.re 485154 bra breasts nipples nurse thighhighs.png', u_file.get_file_name_from_url(url))


def test_download_file():
    url = 'http://aod.cos.tx.xmcdn.com/group20/M01/7E/F8/wKgJJ1eoW8uBquKEACmsecPrn1o863.m4a'
    file_name = '19663334'
    file_path = r'cache'
    u_file.download_file(url, file_name, file_path)
    u_unittest.assert_true(os.path.isfile(r'cache\19663334.m4a'))


def test_get_all_sub_files():
    root_path = r'D:\BaiduNetdiskDownload\最新免费国外hdr环境高清贴图批量下载_By佐邦视觉'
    file_paths = u_file.get_all_sub_files(root_path)
    u_log.info('file size: {}'.format(len(file_paths)))


def test_m_get():
    u_unittest.assert_eq(u_file.m_get({'a': {'b': {'c': 1}}}, 'a.b.c', 2), 1)
    u_unittest.assert_eq(u_file.m_get({'a': {'b': {'c': 1}}}, 'a.b.d', 2), 2)

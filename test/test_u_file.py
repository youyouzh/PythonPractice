#!/usr/bin/python
# -*- coding: utf-8 -*
import os

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


# 批量修改图片后缀名，垃圾微信报错GIF图片有问题
def test_modify_picture_suffix():
    source_directory = r'D:\data\HDRI贴图资源\专业4K全景HDRI贴图合辑\HDR'
    sub_file_paths = u_file.get_all_sub_files(source_directory)
    for sub_file_path in sub_file_paths:
        if os.path.isdir(sub_file_path):
            u_log.info('The file is directory: {}'.format(sub_file_path))
            continue
        if os.path.getsize(sub_file_path) < 5e6:
            u_log.info('The file size is small. file: {}, size: {}'.format(sub_file_path, os.path.getsize(sub_file_path)))
            continue
        sub_file_name = os.path.split(sub_file_path)[1]
        sub_file_name_suffix = os.path.splitext(sub_file_name)[1]

        move_target_file_path = sub_file_path.replace(sub_file_name_suffix, ".gif")
        u_log.info('move file: {} --> file: {}'.format(sub_file_path, move_target_file_path))
        os.replace(sub_file_path, move_target_file_path)


# 遍历所有子文件，然后移动到另一个地方
def test_collect_sub_files():
    source_root_directory = r'D:\data\HDRI贴图资源\专业4K全景HDRI贴图合辑\HDR'
    move_target_directory = r'D:\data\HDRI贴图资源\专业4K全景HDRI贴图合辑'
    if not os.path.isdir(move_target_directory):
        # 文件不存在则创建
        os.makedirs(move_target_directory)
    sub_file_paths = u_file.get_all_sub_files(source_root_directory)

    for sub_file_path in sub_file_paths:
        if os.path.isdir(sub_file_path):
            u_log.info('The file is directory: {}'.format(sub_file_path))
            continue
        sub_file_name = os.path.split(sub_file_path)[1]
        sub_file_name_suffix = os.path.splitext(sub_file_name)[1]
        if sub_file_name_suffix != '.jpg' and sub_file_name_suffix != '.hdr':
            u_log.info('The file is not hdr file: {}'.format(sub_file_name))
            continue

        move_target_file_path = os.path.join(move_target_directory, sub_file_name)
        if os.path.isfile(move_target_file_path):
            u_log.warn('The move target file is exist: {}'.format(move_target_file_path))
            continue

        u_log.info('move file: {} --> file: {}'.format(sub_file_path, move_target_file_path))
        os.replace(sub_file_path, move_target_file_path)


def test_replace_file_name():
    source_root_directory = r'D:\BaiduNetdiskDownload\Dutch Skies 360 Volume'
    sub_file_paths = u_file.get_all_sub_files(source_root_directory)

    for sub_file_path in sub_file_paths:
        move_target_file_path = sub_file_path.replace('_佐邦视觉', '')
        if os.path.isfile(move_target_file_path):
            u_log.warn('The target file is exist: {}'.format(move_target_file_path))
            continue

        u_log.info('rename file: {} --> file: {}'.format(sub_file_path, move_target_file_path))
        os.replace(sub_file_path, move_target_file_path)

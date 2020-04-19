#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import numpy as np
import json
from PIL import Image
import u_base.u_log as log

from spider.pixiv.mysql.db import session, Illustration, IllustrationTag
from spider.pixiv.arrange.illust_file import read_file_as_list, collect_illust, get_all_image_file_path, get_illust_id


__all__ = [
    'update_illust_tag',
    'is_special_tag',
    'is_gray',
    'is_small',
    'collect_illusts'
]


# 用来缓存一批 illust_id
cache_illust_ids = []


# 更新本地整理好的插图
def update_illust_tag(directory, tag):
    """
    将某个文件夹下的所有文件在illust数据库中的记录标记score值
    :param directory: 目标文件夹
    :param tag: 某个类型的标记名称
    :param tag: 分数， 8：有用的教程，7：一级棒， 7：很棒， 5：还可以，4：有点色色，3：无感，2：不管了，1：什么鬼不要
    :return:
    """
    if not os.path.exists(directory):
        log.error('The directory is not exist: {}'.format(directory))
        return
    file_names = os.listdir(directory)
    for file_name in file_names:
        # 获取目录或者文件的路径
        if os.path.isdir(os.path.join(directory, file_name)):
            continue
        log.info('process file: ' + file_name)
        # 提取 illust_id
        illust_id = file_name.split('_')[0]
        if not illust_id.isnumeric():
            continue
        illustration: Illustration = session.query(Illustration).get(int(illust_id))
        if illustration is None:
            log.info('The illustration is not exist. illust_id: {}'.format(illust_id))
            continue
        log.info('process illust_id: {}, set tag to: {} '.format(illust_id, tag))
        illustration.tag = tag
        session.commit()


# 是否指定的tag
def is_special_tag(illust_path: str) -> bool:
    move_tags = ['wlop', 'wlop']
    illust_filename = os.path.split(illust_path)[1]
    tags = illust_filename.split('-')  # 从文件名分解得出包含的标签
    for tag in tags:
        for move_tag in move_tags:
            if tag.find(move_tag) >= 0:
                return True
    return False


# 是否黑白灰度图片
def is_gray(illust_path: str) -> bool:
    """
    1、纯彩色，只有白黑二色，白色RGB【R=G=B=255】，色黑【R=G=B=0】；
    2、灰阶，RGB【R=G=B】；
    色偏值 Diff = Max（|R-G|，|R-B|，|G-B|）；
    彩色图片有所图片中最大的 Diff < 50；
    :param illust_path: 图片地址
    :return: True for gray picture
    """
    if not os.path.isfile(illust_path):
        log.error('The file is not exist: {}'.format(illust_path))
        return False
    # if int(os.path.split(illust_path)[1].split('_')[0]) != 64481817:
    #     return False
    threshold = 10  # 判断阈值，图片3个通道间差的方差均值小于阈值则判断为灰度图

    try:
        illust_image = Image.open(illust_path)
    except (Image.UnidentifiedImageError, OSError) as e:
        log.error("read file Error. illust_path: {}".format(illust_path))
        return False
    # 灰度图像
    if len(illust_image.getbands()) <= 2:
        return True

    illust_image.thumbnail((200, 200))  # 缩放，整体颜色信息不变
    channel_r = np.array(illust_image.getchannel('R'), dtype=np.int)
    channel_g = np.array(illust_image.getchannel('G'), dtype=np.int)
    channel_b = np.array(illust_image.getchannel('B'), dtype=np.int)
    diff_sum = (channel_r - channel_g).var() + (channel_g - channel_b).var() + (channel_b - channel_r).var()
    return diff_sum <= threshold


# 是否图片太小
def is_small(illust_path: str) -> bool:
    min_image_size = 1e5  # 小于100k的文件
    return os.path.getsize(illust_path) <= min_image_size


# 图片是否太长
def is_too_long(illust_path: str) -> bool:
    illust_image = Image.open(illust_path)
    width, height = illust_image.size
    return height >= width * 3


# 是否指定的illust_id，用来提取某一个用户或者某一批插画
def is_special_illust_ids(illust_path: str = None, **kwargs) -> bool:
    user_id = kwargs.get('user_id')
    if not user_id:
        log.error('The user_id is empty.')
        return False
    cache_illust_ids_path = r'.\cache\\' + str(user_id) + '-illust-ids.json'
    if not os.path.isfile(cache_illust_ids_path):
        # 某个用户的illust_id
        illust_ids = session.query(Illustration.id).filter(Illustration.user_id == user_id)\
            .order_by(Illustration.total_bookmarks.desc()).all()
        illust_ids = [x.id for x in illust_ids]
        log.info('query user_id: {}, illust_ids: {}'.format(user_id, illust_ids))
        json.dump(illust_ids, open(cache_illust_ids_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    else:
        illust_ids = json.load(open(cache_illust_ids_path, 'r', encoding='utf-8'))
    current_illust_id = get_illust_id(illust_path)
    return current_illust_id in illust_ids


# 提取某个文件夹下面收藏TOP的图片
def extract_top(illust_path: str, count: int):
    if not os.path.isdir(illust_path):
        log.error('The illust path is not exist: {}'.format(illust_path))
        return
    illust_files = os.listdir(illust_path)
    log.info('The illust size is: {}'.format(len(illust_files)))
    top_directory = os.path.join(illust_path, 'top')
    if not os.path.isdir(top_directory):
        log.info('create top directory: {}'.format(top_directory))
        os.makedirs(top_directory)

    illustrations: [Illustration] = []
    for illust_file in illust_files:
        if os.path.isdir(illust_file):
            log.info('The file is directory: {}'.format(illust_file))
            continue
        illust_id = get_illust_id(illust_file)
        if illust_id <= 0:
            log.error('The illust_id is is not exist: {}'.format(illust_file))
            continue
        illustrations.append(session.query(Illustration).get(illust_id))
    illustrations.sort(key=lambda x: x.total_bookmarks, reverse=True)
    illustrations = illustrations[:count]
    top_illust_ids = set(x.id for x in illustrations)
    log.info('The top illust ids is: {}'.format(top_illust_ids))
    for illust_file in illust_files:
        if get_illust_id(illust_file) in top_illust_ids:
            log.info('ready move top file: {}'.format(illust_file))
            source_file_path = os.path.join(illust_path, illust_file)
            source_file_path = os.path.abspath(source_file_path)
            move_target_path = os.path.join(top_directory, illust_file)
            move_target_path = os.path.abspath(move_target_path)
            log.info('move file: {} --> {}'.format(source_file_path, move_target_path))
            os.replace(source_file_path, move_target_path)


# 移动、统一、分类文件
def collect_illusts(collect_tag='back', collect_function=None, max_collect_count=10, **kwargs):
    illust_paths = get_all_image_file_path()

    collect_count = 0
    for illust_path in illust_paths:
        if not os.path.isfile(illust_path):
            log.error('The file is not exist: {}'.format(illust_path))
            continue
        if collect_function(illust_path, **kwargs):
            collect_illust(collect_tag, illust_path)
            collect_count += 1
        if collect_count >= max_collect_count:
            break
    log.info('----> total move file count: {}'.format(collect_count))


if __name__ == '__main__':
    user_id = 55460411
    collect_illusts(str(user_id), is_special_illust_ids, 1000, user_id=user_id)
    # target_directory = r'..\crawler\result\illusts\score-3-无感'
    # update_illust_tag(target_directory, 'ignore')
    # collect_illust_by_collect_function(is_gray)
    # extract_top(target_directory, 20)

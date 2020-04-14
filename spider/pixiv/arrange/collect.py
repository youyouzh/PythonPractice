#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import numpy as np
from PIL import Image

from spider.pixiv.mysql.db import session, Illustration, IllustrationTag
from spider.pixiv.arrange.illust_file import read_file_as_list, collect_illust, get_all_image_file_path


# 更新本地整理好的插图
def update_illust_score():
    # 目标文件夹
    directory = r"result\collect\初音未来"
    score = 5   # 分数， 8：有用的教程，7：一级棒， 7：很棒， 5：还可以，4：有点色色，3：无感，2：不管了，1：什么鬼不要
    if not os.path.exists(directory):
        print('The directory is not exist. ' + directory)
        return
    file_names = os.listdir(directory)
    for file_name in file_names:
        # 获取目录或者文件的路径
        if os.path.isdir(os.path.join(directory, file_name)):
            continue
        print('process file: ' + file_name)
        # 提取 illust_id
        illust_id = file_name.split('_')[0]
        if not illust_id.isnumeric():
            continue
        illustration: Illustration = session.query(Illustration).get(int(illust_id))
        if illustration is None:
            print('The illustration is not exist. illust_id: ' + illust_id)
            continue
        if illustration.score > 0:
            print("The illustration is exist. score: " + str(illustration.score))
            continue
        print('process illust_id: %s, set score to: %d ' % (illust_id, score))
        illustration.score = score
        session.commit()


# 是否指定的tag
def is_special_tag(illust_path: str):
    move_tags = ['wlop', 'wlop']
    illust_filename = os.path.split(illust_path)[1]
    tags = illust_filename.split('-')  # 从文件名分解得出包含的标签
    for tag in tags:
        for move_tag in move_tags:
            if tag.find(move_tag) >= 0:
                return True
    return False


# 是否黑白灰度图片
def is_gray(illust_path: str):
    """
    1、纯彩色，只有白黑二色，白色RGB【R=G=B=255】，色黑【R=G=B=0】；
    2、灰阶，RGB【R=G=B】；
    色偏值 Diff = Max（|R-G|，|R-B|，|G-B|）；
    彩色图片有所图片中最大的 Diff < 50；
    :param illust_path: 图片地址
    :return: True for gray picture
    """
    if not os.path.isfile(illust_path):
        print('The file is not exist')
        return False
    # if int(os.path.split(illust_path)[1].split('_')[0]) != 64481817:
    #     return False
    threshold = 10  # 判断阈值，图片3个通道间差的方差均值小于阈值则判断为灰度图

    try:
        illust_image = Image.open(illust_path)
    except (Image.UnidentifiedImageError, OSError) as e:
        print("read file Error. " + illust_path)
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
def is_small(illust_path: str):
    min_image_size = 1e5  # 小于100k的文件
    return os.path.getsize(illust_path) <= min_image_size


# 移动、统一、分类文件
def collect_illusts(collect_tag='back', collect_function=None, max_collect_count=10):
    illust_paths = get_all_image_file_path()

    collect_count = 0
    for illust_path in illust_paths:
        if not os.path.isfile(illust_path):
            print('The file is not exist.', illust_path)
            continue
        if collect_function(illust_path):
            collect_illust(collect_tag, illust_path)
            collect_count += 1
        if collect_count >= max_collect_count:
            break
    print('----> total move file count: %d' % collect_count)


if __name__ == '__main__':
    collect_illusts('small', is_small, 10000)
    # collect_illust_by_collect_function(is_gray)
    # update_illust_score()

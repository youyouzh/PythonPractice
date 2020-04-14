#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import numpy as np
import cv2
import json
from PIL import Image

from spider.pixiv.mysql.db import session, Illustration, IllustrationTag
from spider.pixiv.arrange.illust_file import read_file_as_list


# 更新本地整理好的插图
def arrange():
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


# 线稿：黑色占比非常低
def is_line(channel_r, channel_g, channel_b):
    return False


def read_rgb_by_pil(illust_path):
    illust_image = Image.open(illust_path)
    # 灰度图像
    if len(illust_image.getbands()) <= 2:
        return True
    channel_r = np.array(illust_image.getchannel('R'), dtype=np.int)
    channel_g = np.array(illust_image.getchannel('G'), dtype=np.int)
    channel_b = np.array(illust_image.getchannel('B'), dtype=np.int)
    return channel_r, channel_g, channel_b


def read_rgb_by_cv(illust_path):
    # 因为window编码问题，不能使用 cv2.imread(illust_path), 会返回 None
    # 此时返回的是一个ndarray
    illust_image = cv2.imdecode(np.fromfile(illust_path, dtype=np.int), cv2.IMREAD_COLOR)
    # if illust_image.type() == cv2.CV_8UC1:
    #     return True
    channel_b, channel_g, channel_r = cv2.split(illust_image)
    return channel_r, channel_g, channel_b


# 移动、统一、分类文件
def collect_illusts(collect_function):
    base_directory = r'..\crawler\result\illusts'
    base_directory = os.path.abspath(base_directory)
    illust_directories = ['10000-20000', '100000-200000', '20000-30000', '200000-300000', '30000-40000',
                          '300000-400000', '40000-50000', '5000-6000', '50000-60000', '6000-7000', '60000-70000',
                          '7000-8000', '70000-80000', '8000-9000', '80000-90000', '9000-10000', '90000-100000']

    move_target_directory = r'..\crawler\result\collect\gray'
    move_target_directory = os.path.abspath(move_target_directory)
    if not os.path.exists(move_target_directory):
        print('The directory is not exist. create: ' + move_target_directory)
        os.makedirs(move_target_directory)

    checked_file_path = r'..\crawler\result\collect\gray\checked_file.txt'
    checked_file_path = os.path.abspath(checked_file_path)
    checked_files = read_file_as_list(checked_file_path)
    checked_files = set(checked_files)
    checked_file_handle = open(checked_file_path, 'w+', encoding='utf-8')

    move_file_count = 0
    max_move_count = 1000
    for illust_directory in illust_directories:
        illust_directory = base_directory + '\\' + illust_directory
        illust_files = os.listdir(illust_directory)
        print('illust files size: %d' % len(illust_files))
        for illust_file in illust_files:
            full_source_illust_file_path = os.path.join(illust_directory, illust_file)       # 完整的源图片路径
            full_target_illust_file_path = os.path.join(move_target_directory, illust_file)  # 移动目标路径
            print('process file: ' + illust_file)
            if full_source_illust_file_path not in checked_files and collect_function(full_source_illust_file_path):
                move_file_count += 1
                print('find move file(%d): %s' % (move_file_count, full_source_illust_file_path))
                os.replace(full_source_illust_file_path, full_target_illust_file_path)
            checked_file_handle.writelines(full_source_illust_file_path + '\n')
        if move_file_count >= max_move_count:
            break
    print('----> total move file count: %d' % move_file_count)


if __name__ == '__main__':
    # collect_illusts(is_special_tag)
    collect_illusts(is_gray)
    # arrange()

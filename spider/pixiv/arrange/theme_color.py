#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import numpy as np
from PIL import Image
import cv2
import json
import collections
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import u_base.u_log as log
from spider.pixiv.arrange.illust_file import get_illust_file_path, collect_illust, get_illust_id, get_directory_illusts


def show(images, themes):
    figure = plt.figure()
    gs = gridspec.GridSpec(len(images), len(themes) + 1)
    for image_index in range(len(images)):
        image_figure = figure.add_subplot(gs[image_index, 0])
        image_figure.imshow(images[image_index])
        image_figure.set_title("Image %s" % str(image_index + 1))
        image_figure.xaxis.set_ticks([])
        image_figure.yaxis.set_ticks([])

        current_image_themes = themes[image_index]
        pale = np.zeros(images[image_index].shape, dtype=np.int)
        h, w, _ = pale.shape
        ph = h / len(current_image_themes)
        for y in range(h):
            pale[y, :, :] = np.array(current_image_themes[int(y / ph)], dtype=np.int)
        pl = figure.add_subplot(gs[image_index, 1])
        pl.imshow(pale)
        pl.xaxis.set_ticks([])
        pl.yaxis.set_ticks([])
    plt.show()


def show_by_illust_id(illust_id: int):
    """
    显示指定插画
    :param illust_id: 插画id
    :return: None
    """
    illust_path = get_illust_file_path(illust_id)
    illust_image = Image.open(illust_path)
    illust_pixel_matrix = np.array(illust_image)
    log.info("illust path: {}, pixel shape: {}".format(illust_path, illust_pixel_matrix.shape))

    plt.figure('Image')
    plt.imshow(illust_image)
    plt.axis('on')
    plt.title('illust_id: %d, width: %d, height: %d' % (illust_id, illust_image.size[0], illust_image.size[1]))
    plt.show()


def rgb_kmeans(illust_path: str, show_image=False):
    """
    K-Means聚类图片的颜色
    :param show_image: 是否显示训练效果
    :param illust_path: 图片地址
    :return:
    """
    max_color = 5
    illust_image = Image.open(illust_path)
    illust_image.thumbnail((200, 200))  # 缩放，整体颜色信息不变
    illust_pixel_matrix = np.array(illust_image)
    log.info('begin k-means. image shape: {}, image path: {}'.format(illust_pixel_matrix.shape, illust_path))

    # 展开所有像素点用于聚类
    # 为了加快聚类速度，对图片进行缩放，主要颜色信息的分布基本没有变化
    height, width, pixel = illust_pixel_matrix.shape
    pixel_data = np.reshape(illust_pixel_matrix, (height * width, pixel))

    # KMeans 聚合像素，提取主题颜色
    km = KMeans(n_clusters=max_color)
    km.fit(pixel_data)
    clusters = np.array(km.cluster_centers_, dtype=np.int)
    log.info('k-means end.')

    # 每个聚类的数量
    label_count = collections.Counter(km.labels_)
    log.info('clusters: {}, label_count: {}'.format(clusters, dict(label_count)))

    if show_image:
        show([illust_pixel_matrix], [clusters])
    return clusters, label_count


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
    # 因为window中文编码问题，不能使用 cv2.imread(illust_path), 会返回 None
    # 此时返回的是一个ndarray
    illust_image = cv2.imdecode(np.fromfile(illust_path, dtype=np.int), cv2.IMREAD_COLOR)
    # if illust_image.type() == cv2.CV_8UC1:
    #     return True
    # height, width, _ = illust_image.shape
    # base_height = 256
    # resize_image = cv2.resize(illust_image, (int(width * base_height / height), base_height))
    # height, width, channel = resize_image.shape
    channel_b, channel_g, channel_r = cv2.split(illust_image)
    return channel_r, channel_g, channel_b


def hsv_kmeans(image):
    # hsv空间是圆锥体，不能用KMeans聚合
    height, width, channel = image.shape
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv = hsv.reshape((height * width, channel))

    log.info('begin k-means')
    cluster_count = 4
    km = KMeans(n_clusters=cluster_count)
    km.fit(hsv)
    themes = np.array(km.cluster_centers_, dtype=np.uint8)  # 必须是 np.uint8 类型
    log.info('end k-means, clusters is: {}'.format(themes))
    themes = themes.reshape((1, cluster_count, 3))  # 必须转为三维才能进行 cvtColor
    themes = cv2.cvtColor(themes, cv2.COLOR_HSV2RGB)
    themes = themes.reshape((cluster_count, 3))
    log.info(themes)
    return themes


def train_main_colors(illust_directory):
    log.info('begin train main colors.')
    save_cache_file = r'.\cache\main_color.txt'
    # save_cache_file_handle = open(save_cache_file, 'w+', encoding='utf-8')
    illust_main_colors = {}
    if os.path.isfile(save_cache_file):
        illust_main_colors = json.load(open(save_cache_file, 'r', encoding='utf-8'))
    illust_files = os.listdir(illust_directory)
    for illust_file in illust_files:
        illust_file = os.path.join(illust_directory, illust_file)
        if os.path.isdir(illust_file):
            log.info('The file is directory: {}'.format(illust_file))
            continue
        illust_id = get_illust_id(illust_file)
        if illust_id is None:
            log.info('The file illust_id is None: {}'.format(illust_file))
            continue
        if str(illust_id) in illust_main_colors:
            log.info('The file has been trained: {}'.format(illust_file))
            continue
        clusters, label_count = rgb_kmeans(illust_file)
        main_colors = []
        for label in label_count:
            main_colors.append({
                'illust_id': illust_id,
                'index': int(label),
                'count': label_count[label],
                'color': clusters[label].tolist()
            })
        main_colors.sort(key=lambda x: x['count'], reverse=True)
        illust_main_colors[illust_id] = main_colors
        json.dump(illust_main_colors, open(save_cache_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    log.info('end train main colors.')
    return illust_main_colors


def classify_main_color(illust_directory):
    log.info('begin classify main colors.')
    train_result_file = r'.\cache\main_color.txt'
    collect_directory = r'..\crawler\result\illusts\30000-40000\white'
    if not os.path.isdir(collect_directory):
        os.makedirs(collect_directory)

    if not os.path.isfile(train_result_file):
        log.error('The train result file is not exist: {}'.format(train_result_file))
        return
    log.info('read train info finish.')
    illust_main_colors = json.load(open(train_result_file, 'r', encoding='utf-8'))
    for illust_id in illust_main_colors:
        main_colors = illust_main_colors[illust_id]
        main_colors.sort(key=lambda x: x['count'], reverse=True)

    illust_files = get_directory_illusts(illust_directory)
    for illust_file in illust_files:
        illust_id = illust_file['illust_id']
        if str(illust_id) not in illust_main_colors:
            log.warn('The illust has not main colors info. illust_id: {}'.format(illust_id))
            continue
        main_colors = illust_main_colors[str(illust_id)]
        if min(main_colors[0]['color']) > 220 and min(main_colors[1]['color']) > 200 and min(main_colors[2]['color']) > 200:
            # 主要颜色是白色
            log.info('white illust. collect: {}'.format(illust_id))
            collect_illust(collect_directory, illust_file['path'])


if __name__ == '__main__':
    log.info("begin process")

    target_directory = r'..\crawler\result\illusts\30000-40000'
    train_main_colors(target_directory)
    # classify_main_color(target_directory)


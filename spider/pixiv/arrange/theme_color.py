#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import numpy as np
from PIL import Image
import cv2
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from spider.pixiv.arrange.illust_file import get_illust_file_path, collect_illust, get_all_image_file_path


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
    illust_path = get_illust_file_path(7996295)
    illust_image = Image.open(illust_path)
    illust_pixel_matrix = np.array(illust_image)
    print("illust path: ", illust_path)
    print("pixel shape: ", illust_pixel_matrix.shape)
    collect_illust('temp', illust_path)

    plt.figure('Image')
    plt.imshow(illust_image)
    plt.axis('on')
    plt.title('illust_id: %d, width: %d, height: %d' % (illust_id, illust_image.size[0], illust_image.size[1]))
    plt.show()


# [[ 43  62  82]
#  [247 226 218]
#  [ 82 178 177]
#  [189 137 139]
#  [178 219 204]]
def extract(illust_path: str):
    """
    提取指定图片的主题色
    :param illust_path:
    :return:
    """
    max_color = 5
    illust_image = Image.open(illust_path)
    illust_pixel_data = np.array(illust_image)
    print(illust_pixel_data.shape)

    # 展开所有像素点
    height, width, pixel = illust_pixel_data.shape
    pixel_data = np.reshape(illust_pixel_data, (height * width, pixel))

    # KMeans 聚合像素，提取主题颜色
    km = KMeans(n_clusters=max_color)
    km.fit(pixel_data)
    themes = np.array(km.cluster_centers_, dtype=np.int)
    # themes = np.array([[43, 62, 82], [247, 226, 218], [82, 178, 177], [189, 137, 139], [178, 219, 204]])
    print(themes)
    show([illust_pixel_data], [themes])
    return themes


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


def check_too_height_illust():
    """
    检查特别高的插画
    :return:
    """
    illust_paths = get_all_image_file_path()
    for illust_path in illust_paths:
        if os.path.getsize(illust_path) < 1e5:
            # 小于100kb的文件
            print('The file is too small.', illust_path)
            continue
        illust_image = Image.open(illust_path)
        width, height = illust_image.size
        if height >= width * 3:
            print(illust_path, width, height)


if __name__ == '__main__':
    check_too_height_illust()

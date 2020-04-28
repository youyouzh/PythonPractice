import os
import cv2
import PIL
import collections
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from PIL import Image


import u_base.u_log as log

__all__ = [
    'show_color_space_3d',
    'extract_main_color',
    'get_color_by_hsv',
    'pil_to_cv2_image',
    'cv_to_pil_image',
    'get_image',
    'show_hist'
]

COLOUR_HSV_RANGE = {
    'red': {
        'h': [{'min': 0, 'max': 10}, {'min': 156, 'max': 180}],
        's': [{'min': 43, 'max': 255}],
        'v': [{'min': 46, 'max': 255}]
    },
    'orange': {
        'h': [{'min': 11, 'max': 25}],
        's': [{'min': 43, 'max': 255}],
        'v': [{'min': 46, 'max': 255}]
    },
    'yellow': {
        'h': [{'min': 26, 'max': 34}],
        's': [{'min': 43, 'max': 255}],
        'v': [{'min': 46, 'max': 255}]
    },
    'green': {
        'h': [{'min': 35, 'max': 77}],
        's': [{'min': 43, 'max': 255}],
        'v': [{'min': 46, 'max': 255}]
    },
    'cyan': {
        'h': [{'min': 78, 'max': 99}],
        's': [{'min': 43, 'max': 255}],
        'v': [{'min': 46, 'max': 255}]
    },
    'blue': {
        'h': [{'min': 100, 'max': 124}],
        's': [{'min': 43, 'max': 255}],
        'v': [{'min': 46, 'max': 255}]
    },
    'purple': {
        'h': [{'min': 125, 'max': 155}],
        's': [{'min': 43, 'max': 255}],
        'v': [{'min': 46, 'max': 255}]
    },
}
BLACK_WHITE_HSV_RANGE = {
    'black': {
        'h': [{'min': 0, 'max': 180}],
        's': [{'min': 0, 'max': 255}],
        'v': [{'min': 0, 'max': 46}]
    },
    'gray': {
        'h': [{'min': 0, 'max': 180}],
        's': [{'min': 0, 'max': 43}],
        'v': [{'min': 46, 'max': 255}]
    },
    'white': {
        'h': [{'min': 0, 'max': 180}],
        's': [{'min': 0, 'max': 30}],
        'v': [{'min': 221, 'max': 255}]
    }
}


def show_color_space_3d(image_path, hsv: bool = False):
    """
    在3D界面展示图片像素颜色空间分布
    :param image_path: 图片地址
    :param hsv: 是否hsv颜色空间
    :return:
    """
    log.info('begin show rgb space.')
    # 读取图片，压缩，点太多会卡死
    pixel_colors = get_image(image_path, ndarray=True, thumbnail_size=(100, 100))
    log.info('read image success: {}'.format(image_path))
    r, g, b = cv2.split(pixel_colors)

    # 颜色归一化
    width, height, channel = pixel_colors.shape
    dot_color = pixel_colors.reshape(width * height, channel)
    norm = colors.Normalize(vmin=-1., vmax=1.)
    norm.autoscale(dot_color)
    dot_color = norm(dot_color).tolist()

    fig = plt.figure()
    axis = fig.add_subplot(1, 1, 1, projection="3d")

    if hsv:
        h, s, v = cv2.split(cv2.cvtColor(pixel_colors, cv2.COLOR_RGB2HSV))
        axis.scatter(h, s, v, facecolors=dot_color, marker=".")
        axis.set_xlabel("Hue")
        axis.set_ylabel("Saturation")
        axis.set_zlabel("Value")
        plt.show()
        return

    axis.scatter(r, g, b, facecolors=dot_color, marker=".")
    axis.set_xlabel("Red")
    axis.set_ylabel("Green")
    axis.set_zlabel("Blue")
    plt.show()


def show_hist(image_path: str):
    """
    显示图片的RGB直方图
    :param image_path: 图片地址
    :return:
    """
    log.info('begin show hist.')
    # 读取图片，压缩，点太多会卡死
    pixel_colors = get_image(image_path, ndarray=False, thumbnail_size=(200, 200))
    log.info('read image success: {}'.format(image_path))
    r, g, b = pixel_colors.split()
    plt.figure('image: ' + os.path.split(image_path)[1])
    plt.hist(np.array(r).flatten(), bins=256, facecolor='r', edgecolor='r')
    plt.hist(np.array(g).flatten(), bins=256, facecolor='g', edgecolor='g')
    plt.hist(np.array(b).flatten(), bins=256, facecolor='b', edgecolor='b')
    plt.show()


def extract_main_color(image_path):
    """
    提取图片的主要颜色
    :param image_path: 图片地址
    :return:
    """
    log.info('begin extract_main_color: {}'.format(image_path))
    pixel_colors = get_image(image_path, ndarray=True, thumbnail_size=(500, 500))
    width, height, channel = pixel_colors.shape
    log.info('read image success: {}'.format(image_path))
    # hsv空间提取颜色
    h, s, v = cv2.split(cv2.cvtColor(pixel_colors, cv2.COLOR_RGB2HSV))

    h = np.reshape(h, width * height)
    h_to_count = collections.Counter(h)  # 这样很快

    color_point = {}
    for point_h in h_to_count:
        color = get_color_by_hsv(point_h)
        if color in color_point:
            color_point[color] += h_to_count[point_h]
        else:
            color_point[color] = h_to_count[point_h]
    log.info('The picture color distribution: {}'.format(color_point))
    # sorted(color_point.items(), key=lambda x: x[1], reverse=True)   # 颜色从高到低排序
    main_color_proportion_threshold = 0.5
    for color in color_point:
        if color_point[color] >= width * height * main_color_proportion_threshold:
            log.info('--------> get main color: {}, path: {}'.format(color, image_path))
            return color
    log.info('The picture has not main color. {}'.format(image_path))
    return None


def get_color_by_hsv(h: int, s: int = None, v: int = None):
    """
    通过HSV获取所属颜色
    :param h: 色调分量
    :param s: 饱和度分量
    :param v: 明度分量
    :return: 颜色字符串
    """
    for color in COLOUR_HSV_RANGE:
        for color_h in COLOUR_HSV_RANGE.get(color).get('h'):
            if color_h.get('min') <= h <= color_h.get('max'):
                return color


def get_image(image_path, **kwargs):
    """
    使用PIL读取图片
    :param image_path: 图片地址
    :param thumbnail_size: 压缩大小，以最大的那一个维度为基准等比例压缩，不会导致图片拉伸
    :param resize_size: 严格按照给定大小压缩，会导致拉伸
    :param gray: 是否转换为灰度图
    :return: 返回Image对象
    """
    if not os.path.isfile(image_path):
        log.error('The image file is not exist. file: {}'.format(image_path))
        return None
    file_handler = open(image_path, 'rb')
    try:
        image = Image.open(file_handler).convert('RGB')  # 转为RGB
    except PIL.UnidentifiedImageError:
        log.error('read image failed. path: {}'.format(image_path))
        return None
    if kwargs.get('thumbnail_size') is not None:
        # 等比例缩放
        image.thumbnail(kwargs.get('thumbnail_size'))
    if kwargs.get('resize_size') is not None:
        # 待拉伸缩放
        image = image.resize(kwargs.get('resize_size'))
    # if len(image.getbands()) == 4:
    #     # 4通道转三通道： RGBA -> RGB
    #     image = image.convert('RGB')
    if kwargs.get('gray'):
        image = image.convert('L')
    file_handler.close()  # 及时关闭
    if kwargs.get('ndarray'):
        return np.array(image)
    else:
        return image


def pil_to_cv2_image(image, show=False):
    # PIL Image转换成OpenCV格式
    change_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    if show:
        plt.subplot(121)
        plt.imshow(image)
        plt.subplot(122)
        plt.imshow(change_image)
        plt.show()
    return change_image


def cv_to_pil_image(image, show=False):
    # OpenCV图片转换为PIL image
    change_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    if show:
        plt.subplot(121)
        plt.imshow(image)
        plt.subplot(122)
        plt.imshow(change_image)
        plt.show()
    return change_image


if __name__ == '__main__':
    image_path = r'H:\Pictures\动漫插画\ssim\Wallpapers_111.png'
    # show_color_space_3d(image_path, True)
    show_hist(image_path)

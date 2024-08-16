import os
import cv2
import PIL
import collections
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from PIL import Image


from u_base.u_log import logger as log

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


# 是否特定颜色
def is_main_color(illust_path: str, color: str) -> bool:
    return extract_main_color(illust_path) == color


# 判断是否特别的image，需要读取图像RGB信息
def is_special_image(illust_path: str, **kwargs) -> bool:
    file_handle = open(illust_path, 'rb')
    image = Image.open(file_handle)
    file_handle.close()  # 必须关闭文件句柄，否则无法移动文件
    return False


# 图片是否太长
def is_too_long(illust_path: str) -> bool:
    illust_image = Image.open(illust_path)
    width, height = illust_image.size
    return height >= width * 3


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
    path = r'H:\Pictures\动漫插画\ssim\Wallpapers_111.png'
    # show_color_space_3d(image_path, True)
    show_hist(path)

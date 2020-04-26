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
    'get_color_by_hsv',
    'pil_to_cv2_image',
    'cv_to_pil_image',
    'get_image',
    'a_hash',
    'p_hash',
    'd_hash',
    'camp_hash'
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


def extract_main_color(image_path):
    log.info('begin extract_main_color: {}'.format(image_path))
    pixel_colors = get_image(image_path, ndarray=True, thumbnail_size=(500, 500))
    width, height, channel = pixel_colors.shape
    log.info('read image success: {}'.format(image_path))
    # hsv空间提取颜色
    h, s, v = cv2.split(cv2.cvtColor(pixel_colors, cv2.COLOR_RGB2HSV))

    h = np.reshape(h, width * height)
    color_point = {}
    for point_h in h:
        color = get_color_by_hsv(point_h)
        if color in color_point:
            color_point[color] += 1
        else:
            color_point[color] = 1
    log.info('end extract main color: {}'.format(image_path))


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


def a_hash(image):
    """
    平均哈希算法（aHash）,该算法是基于比较灰度图每个像素与平均值来实现。
    aHash的hanming距离步骤：
    1. 先将图片压缩成8*8的小图
    2. 将图片转化为灰度图
    3. 计算图片的Hash值，这里的hash值是64位，或者是32位01字符串
    4. 将上面的hash值转换为16位的
    5. 通过hash值来计算汉明距离
    :param image:
    :return: hash_str
    """
    # 将图片缩放为8*8的
    image = cv2.resize(image, (8, 8), interpolation=cv2.INTER_CUBIC)
    # 将图片转化为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # s为像素和初始灰度值，hash_str为哈希值初始值
    s = 0
    # 遍历像素累加和
    for i in range(8):
        for j in range(8):
            s = s + gray[i, j]
    # 计算像素平均值
    avg = s / 64
    # 灰度大于平均值为1相反为0，得到图片的平均哈希值，此时得到的hash值为64位的01字符串
    ahash_str = ''
    for i in range(8):
        for j in range(8):
            if gray[i, j] > avg:
                ahash_str = ahash_str + '1'
            else:
                ahash_str = ahash_str + '0'
    result = ''
    for i in range(0, 64, 4):
        result += ''.join('%x' % int(ahash_str[i: i + 4], 2))
    log.info('The image a_hash is: {}'.format(result))
    return result


def d_hash(image):
    """
    差异值哈希算法（dHash）：
    相比pHash，dHash的速度要快的多，相比aHash，dHash在效率几乎相同的情况下的效果要更好，它是基于渐变实现的。
    dHash的hanming距离步骤：
    1. 先将图片压缩成9*8的小图，有72个像素点
    2. 将图片转化为灰度图
    3. 计算差异值：dHash算法工作在相邻像素之间，这样每行9个像素之间产生了8个不同的差异，一共8行，则产生了64个差异值，或者是32位01字符串。
    4. 获得指纹：如果左边的像素比右边的更亮，则记录为1，否则为0.
    5. 通过hash值来计算汉明距离
    :param image:
    :return: hash_str
    """
    image = cv2.resize(image, (9, 8))
    # 转换灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hash_str = ''
    # 每行前一个像素大于后一个像素为1，相反为0，生成哈希
    for i in range(8):
        for j in range(8):
            if gray[i, j] > gray[i, j + 1]:
                hash_str = hash_str + '1'
            else:
                hash_str = hash_str + '0'
    result = ''
    for i in range(0, 64, 4):
        result += ''.join('%x' % int(hash_str[i: i + 4], 2))
    log.info('The image d_hash is: {}'.format(result))
    return result


def p_hash(image):
    """
    感知哈希算法（pHash）
    均值哈希虽然简单，但是受均值影响大。如果对图像进行伽马校正或者进行直方图均值化都会影响均值，从而影响哈希值的计算。所以就有人提出更健壮的方法，通过离散余弦（DCT）进行低频提取。
    离散余弦变换（DCT）是种图像压缩算法，它将图像从像素域变换到频率域。然后一般图像都存在很多冗余和相关性的，所以转换到频率域之后，只有很少的一部分频率分量的系数才不为0，大部分系数都为0（或者说接近于0）。Phash哈希算法过于严格，不够精确，更适合搜索缩略图，为了获得更精确的结果可以选择感知哈希算法，它采用的是DCT（离散余弦变换）来降低频率的方法。
    pHash的hanming距离步骤：
    1. 缩小图片：32 * 32是一个较好的大小，这样方便DCT计算转化为灰度图
    2. 计算DCT：利用Opencv中提供的dct()方法，注意输入的图像必须是32位浮点型，所以先利用numpy中的float32进行转换
    3. 缩小DCT：DCT计算后的矩阵是32 * 32，保留左上角的8 * 8，这些代表的图片的最低频率
    4. 计算平均值：计算缩小DCT后的所有像素点的平均值。
    5. 进一步减小DCT：大于平均值记录为1，反之记录为0.
    6. 得到信息指纹：组合64个信息位，顺序随意保持一致性。
    7. 最后比对两张图片的指纹，获得汉明距离即可。
    :param image:
    :return:
    """
    # 加载并调整图片为32*32的灰度图片
    resize_image = cv2.resize(image, (32, 32), cv2.COLOR_RGB2GRAY)

    # 创建二维列表
    h, w = image.shape[:2]
    vis0 = np.zeros((h, w), np.float32)
    vis0[:h, :w] = resize_image

    # DCT二维变换
    # 离散余弦变换，得到dct系数矩阵
    img_dct = cv2.dct(cv2.dct(vis0))
    img_dct.resize(8, 8)
    # 把list变成一维list
    img_list = np.array().flatten(img_dct.tolist())
    # 计算均值
    img_mean = cv2.mean(img_list)
    avg_list = ['0' if i < img_mean else '1' for i in img_list]
    result = ''.join(['%x' % int(''.join(avg_list[x:x + 4]), 2) for x in range(0, 64, 4)])
    log.info('The image p_hash is: {}'.format(result))
    return result


def camp_hash(hash1, hash2):
    """
    计算两个哈希值之间的差异
    :param hash1: hash1
    :param hash2: hash2
    :return: distancee 值越小越相似
    """
    distance = 0
    # hash长度不同返回-1,此时不能比较
    if len(hash1) != len(hash2):
        return -1
    # 如果hash长度相同遍历长度
    for i in range(len(hash1)):
        if hash1[i] != hash2[i]:
            distance = distance + 1
    return distance


if __name__ == '__main__':
    image_path = r'H:\Pictures\动漫插画\ssim\Wallpapers_111.png'
    # show_color_space_3d(image_path, True)
    extract_main_color(image_path)

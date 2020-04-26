import os

from spider.pixiv.arrange.image_util import *
from u_base import u_unittest


def test_get_image():
    image_path = r'H:\Pictures\动漫插画\初音未来-miku\comic_louli (3366).png'
    width, height = 1366, 768
    image = get_image(image_path)
    u_unittest.assert_eq(width, image.width)
    u_unittest.assert_eq(height, image.height)

    image = get_image(image_path, resize_size=(200, 200))
    u_unittest.assert_eq(200, image.width)
    u_unittest.assert_eq(200, image.height)

    image = get_image(image_path, thumbnail_size=(200, 200))
    u_unittest.assert_eq(200, image.width)


def test_show_rgb_space():
    image_path = r'H:\Pictures\动漫插画\ssim\Wallpapers_111.png'
    show_color_space_3d(image_path)


def test_get_color_by_hsv():
    u_unittest.assert_eq('red', get_color_by_hsv(5))
    u_unittest.assert_eq('red', get_color_by_hsv(160))
    u_unittest.assert_eq('orange', get_color_by_hsv(25))
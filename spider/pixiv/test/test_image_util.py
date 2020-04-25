import os

from spider.pixiv.arrange.image_util import *
from u_base import u_unittest


def test_get_image():
    image_path = r'H:\Pictures\动漫插画\未整理\collect\comic_sight_014.jpg'
    width, height = 1366, 768
    image = get_image(image_path)
    u_unittest.assert_eq(width, image.width)
    u_unittest.assert_eq(height, image.height)

    image = get_image(image_path, resize_size=(200, 200))
    u_unittest.assert_eq(200, image.width)
    u_unittest.assert_eq(200, image.height)

    image = get_image(image_path, thumbnail_size=(200, 200))
    u_unittest.assert_eq(200, image.width)

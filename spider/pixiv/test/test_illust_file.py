from spider.pixiv.arrange.illust_file import *
from u_base import u_unittest


def test_get_illust_id():
    u_unittest.assert_eq(42344051, get_illust_id(r'G:\Projects\illusts\8000-9000\42344051_p0-3日で消えり.jpg'))
    u_unittest.assert_eq(42344051, get_illust_id(r'42344051_p0-3日で消えり.jpg'))

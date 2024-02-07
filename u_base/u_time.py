#!/usr/bin/python
# -*- coding: utf-8 -*
"""
:desc:
    time related module. looking forward to accepting new patches
"""
import time
from datetime import datetime

__all__ = ['get_str_now']


def get_str_now(fmt='%Y-%m-%d-%H-%M-%S'):
    """
    return string of 'now'

    :param fmt:
        print-format, '%Y-%m-%d-%H-%M-%S' by default
    """
    return str(time.strftime(fmt, time.localtime()))


def get_now_mill_timestamp():
    # 返回现在的毫秒时间戳
    return int(datetime.now().timestamp() * 1000)


if __name__ == '__main__':
    print(get_str_now())

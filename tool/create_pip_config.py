# -*- coding: utf-8 -*-
"""
Python3 --> 解决PIP下载安装速度慢
"""
import os

PATH = f"C:{os.environ['HOMEPATH']}\\pip"
FILE = 'pip.ini'

# 新版ubuntu要求使用https源，要注意。
DICTURL = {
    '清华': 'https://pypi.tuna.tsinghua.edu.cn/simple/',
    '阿里云': 'http://mirrors.aliyun.com/pypi/simple/',
    '中国科技大学': 'https://pypi.mirrors.ustc.edu.cn/simple/',
    '华中理工大学': 'http://pypi.hustunique.com/',
    '山东理工大学': 'http://pypi.sdutlinux.org/',
    '豆瓣': 'http://pypi.douban.com/simple/'
}

# pip.ini 配置文件内容
INFO = f"""[global]
index-url = {DICTURL['阿里云']}
[install]
trusted-host=mirrors.aliyun.com"""

# 判断pip文件夹是否存在，存在跳过，不存在创建
if not os.path.exists(PATH):
    os.mkdir(PATH)
    # 创建配置文件，写入内容
    with open(os.path.join(PATH, FILE), 'w', encoding='utf-8') as f:
        f.write(INFO)
    print(f'用户路径：{PATH}\n配置文件：{FILE}\n****创建成功!****')

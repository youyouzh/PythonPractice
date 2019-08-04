#!/usr/bin/python
# -*- coding: utf-8 -*

import os
from PIL import Image


if __name__ == '__main__':
    path = r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result\images\oshie'
    file_names = os.listdir(path)
    print('image file size: %d' % len(file_names))
    for filename in file_names:
        file_path = path + '\\' + filename
        if os.path.isfile(file_path):
            image = Image.open(file_path)
            # 如果是webp格式转为jpeg格式
            if image.format == 'WEBP':
                image.save(file_path, 'JPEG')
                print('convert image: ' + filename)

#!/usr/bin/python
# -*- coding: utf-8 -*
# file function


import os
import requests
from PIL import Image

import u_base.u_log as log

__all__ = [
    'get_content'
]


def get_content(path):
    if not path:
        return False
    # if path is file, read from file
    if os.path.isfile(path):
        log.info('read content from file: {}'.format(path))
        fin = open(path, 'r', encoding='UTF-8')
        html_content = fin.read()
        fin.close()
        return html_content
    try:
        # herders = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}
        log.info('begin get info from web url: ' + path)
        # time.sleep(0.5)
        response = requests.get(path, timeout=60)
        log.info('end get info from web url: ' + path)
        if not (400 <= response.status_code < 500):
            response.raise_for_status()
        return response.text
    except Exception:
        return False


# download image from url
def download_image(url, path=os.path.curdir, name=None, replace=False, prefix=''):
    """
    download image from url
    :param url: image_url
    :param prefix: image name prefix
    :param path: save directory path
    :param name: image name
    :param replace: replace the same name file.
    :return:
    """
    if not name:
        name = prefix + os.path.basename(url)
    else:
        name = prefix + name

    image_path = os.path.join(path, name)
    if (not os.path.exists(image_path)) or replace:
        # Write stream to file
        log.info('begin download image from url: {}'.format(url))
        try:
            response = requests.get(url, stream=True)
            with open(image_path, 'wb') as out_file:
                out_file.write(response.content)
            del response
        except Exception as e:
            log.error('download image file. {}'.format(e))
            return False
        log.info('end download image. save file: {}'.format(image_path))
    return True


def convert_image_format(image_path, delete=False):
    if not os.path.isfile(image_path):
        log.warn('The image is not exist. path: {}'.format(image_path))
        return None
    image = Image.open(image_path)
    image_format = image.format
    # 如果是webp格式转为jpeg格式
    if image_format == 'WEBP':
        image.save(image_path, 'JPEG')
    image.close()
    if delete:
        os.remove(image_path)

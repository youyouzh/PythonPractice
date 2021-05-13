#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import re
import time
import threadpool

import u_base.u_log as log
from spider.pixiv.mysql.db import session, Illustration, IllustrationTag, IllustrationImage, query_top_total_bookmarks, \
    is_download_user, update_user_tag
from spider.pixiv.pixiv_api import AppPixivAPI, PixivError
from spider.pixiv.arrange.file_util import get_illust_id

CONFIG = json.load(open(os.path.join(os.getcwd(), r'config\config.json')))
_REFRESH_TOKEN = CONFIG.get('token')
_REQUESTS_KWARGS = {
    'proxies': {
      'https': 'http://127.0.0.1:1080',
    },
    # 'verify': False,       # PAPI use https, an easy way is disable requests SSL verify
}


# 下载指定地址的图片，可是指定的URL或者IllustrationImage对象
def download_task(pixiv_api, directory, url=None, illustration_image: IllustrationImage = None):
    save_file_name = None
    begin_time = time.time()

    if not os.path.exists(directory):
        # 递归创建文件夹
        log.info('create directory: {}'.format(directory))
        os.makedirs(directory)
    if url is None or illustration_image is not None:
        # 通过illustration_image下载
        illustration_tags = session.query(IllustrationTag)\
            .filter(IllustrationTag.illust_id == illustration_image.illust_id).all()
        url = illustration_image.image_url_origin
        basename = os.path.basename(url).split('.')
        tags = list()
        for illustration_tag in illustration_tags:
            if illustration_tag.name not in tags:
                tags.append(illustration_tag.name)
        # 过滤掉tag名称中的特殊字符，避免无法创建文件
        save_file_name = re.sub(r"[\\/?*<>|\":]+", '', '-'.join(tags))[0:150]
        save_file_name = str(basename[0]) + '-' + save_file_name + '.' + str(basename[1])

    log.info('begin download image. save file name: {}, download url: {}'.format(save_file_name, url))
    if os.path.isfile(os.path.join(directory, save_file_name)) \
            and os.path.getsize(os.path.join(directory, save_file_name)) >= 200:
        log.info('The illust has been downloaded. file_name: {}'.format(save_file_name))
        return
    try:
        pixiv_api.download(url, '', directory, replace=False, name=save_file_name)
    except (OSError, NameError, PixivError):
        log.error("save error, try again.")
        # 下载失败会生产一个1kb的文件，需要replace=True
        pixiv_api.download(url, '', directory, replace=True, name=save_file_name)
    log.info('download image end. cast: {}, url: {}'.format(time.time() - begin_time, url))


# 使用线程池并行下载
def download_by_pool(directory, urls=None):
    # 创建文件夹
    if not os.path.exists(directory):
        os.makedirs(directory)
    pixiv_api = AppPixivAPI(**_REQUESTS_KWARGS)
    pixiv_api.auth(refresh_token=_REFRESH_TOKEN)
    log.info('begin download image, url size: ' + str(len(urls)))
    pool = threadpool.ThreadPool(8)
    params = map(lambda v: (None, {'pixiv_api': pixiv_api, 'directory': directory, 'url': v}), urls)
    task_list = threadpool.makeRequests(download_task, params)
    [pool.putRequest(task) for task in task_list]
    pool.wait()


# 通过pixiv_id下载图片，从本地数据查找URL，然后下载图片
def download_by_illustration_id(directory: str, illustration_id: int, **kwargs):
    default_kwargs = {
        'spilt_bookmark': False,   # 是否根据收藏量来分割文件夹
        'split_r_18': True,       # 是否把r-18的文件放在单独的文件夹
        'skip_download': True,    # 是否跳过标记为 downloaded 的插画
        'skip_min_width': 800,      # 跳过下载的最小宽度，低于该值的插画不下载
        'skip_min_height': 800,     # 跳过下载的最小长度，低于该值的插画不下载
        'skip_max_page_count': 3,   # 超过多少张画则跳过
        'skip_ignore': True,        # 已经标记为ignore的不下载
    }
    default_kwargs.update(kwargs)
    kwargs = default_kwargs

    pixiv_api = AppPixivAPI(**_REQUESTS_KWARGS)
    pixiv_api.auth(refresh_token=_REFRESH_TOKEN)

    log.info('begin download illust by illustration_id: {}'.format(illustration_id))
    illustration: Illustration = session.query(Illustration).get(illustration_id)
    if illustration is None:
        log.error('The illustration(id: {}) is not exist.'.format(illustration_id))
        return
    illustration_images: [IllustrationImage] = session.query(IllustrationImage)\
        .filter(IllustrationImage.illust_id == illustration_id).all()
    if illustration_images is None or len(illustration_images) == 0:
        log.error('The illustration(id: {}) image is not exist.'.format(illustration_id))
        return

    # 超过3幅的画，大多是漫画类型，先不管
    if len(illustration_images) > kwargs.get('skip_max_page_count'):
        log.warn('The illustration(id: {}) images are more than {}.'
                 .format(illustration_id, kwargs.get('skip_max_page_count')))
        return

    # 过滤长度和宽度
    if illustration.width < kwargs.get('skip_min_width') or illustration.height < kwargs.get('skip_min_height'):
        log.warn('The illustration(id: {}) image is small, width: {}/{}, height: {}/{}'
                 .format(illustration_id, illustration.width, kwargs.get('skip_min_width'),
                         illustration.height, kwargs.get('skip_min_height')))
        return

    # 已经标记为忽略的不下载
    if kwargs.get('skip_ignore') and illustration.tag == 'ignore' or illustration.tag == 'small':
        log.warn('The illustration(id: {}) is ignore.'.format(illustration_id))
        return

    # 按照收藏点赞人数分文件夹
    if kwargs.get('spilt_bookmark'):
        directory += '/' + '-'.join(str(i) for i in get_10_20(illustration.total_bookmarks))

    # R18放在子文件夹
    if kwargs.get('split_r_18') and illustration.r_18 is not None and illustration.r_18 == 1:
        directory += "/r-18"

    for illustration_image in illustration_images:
        if illustration_image.image_url_origin is None or illustration_image.image_url_origin == '':
            log.info('The illustration_image(id: {}) image_url_origin is none.'.format(illustration_id))
            continue
        if kwargs.get('skip_download') and illustration_image.process == 'DOWNLOADED':
            log.info('The illustration_image(id: {}) has been downloaded.'.format(illustration_id))
            continue
        log.info('begin process illust_id: {}, image_url: {}'
                 .format(illustration_image.illust_id, illustration_image.image_url_origin))
        download_task(pixiv_api, directory, illustration_image=illustration_image)
        illustration_image.process = 'DOWNLOADED'
        session.merge(illustration_image)
        session.commit()
        log.info('end process illust_id: {}'.format(illustration_image.illust_id))
    log.info('begin download illust by illustration_id: {}, illust image size: {}'
             .format(illustration_id, len(illustration_images)))


# 下载某个用户的图片，基于本地数据库
def download_by_user_id(save_directory, user_id: int, min_total_bookmarks=5000, **kwargs):
    log.info('begin download illust by user_id: {}'.format(user_id))
    illustrations: [Illustration] = session.query(Illustration)\
        .filter(Illustration.user_id == user_id)\
        .filter(Illustration.total_bookmarks >= min_total_bookmarks)\
        .order_by(Illustration.total_bookmarks.desc()).all()
    if illustrations is None or len(illustrations) <= 0:
        log.warn('The illustrations is empty. user_id: {}'.format(user_id))
        return

    if not os.path.isdir(save_directory):
        os.makedirs(save_directory)

    # 检查当前文件夹，如果文件已经下载则跳过
    download_illust_ids = []
    illust_files = os.listdir(save_directory)
    for illust_file in illust_files:
        # 获取目录或者文件的路径
        if os.path.isdir(os.path.join(save_directory, illust_file)):
            continue

        if os.path.getsize(os.path.join(save_directory, illust_file)) <= 100:
            continue

        # 提取 illust_id
        illust_id = get_illust_id(illust_file)
        if illust_id <= 0:
            log.warn('The file illust_id is not exist. file: {}'.format(illust_file))
            continue
        download_illust_ids.append(illust_id)

    log.info('The illustrations size is: {}'.format(len(illustrations)))
    for illustration in illustrations:
        if illustration.id in download_illust_ids:
            log.info('The illus was downloaded. illust_id: {}'.format(illustration.id))
            continue

        download_by_illustration_id(save_directory, illustration.id, **kwargs)
    update_user_tag(user_id, 'download')
    log.info('end download illust by user_id: {}'.format(user_id))


# 下载某个tag标签的图片，基于本地数据库
def download_by_tag(save_directory, tag: str, min_total_bookmarks=5000):
    log.info('begin download illust by tag: {}'.format(tag))
    illustrations: [Illustration] = session.query(Illustration) \
        .filter(Illustration.id.in_(
            session.query(IllustrationTag.illust_id).filter(IllustrationTag.name == tag))) \
        .filter(Illustration.total_bookmarks >= min_total_bookmarks) \
        .order_by(Illustration.total_bookmarks.desc()).all()
    log.info('The illustration of tag: {} count is: {}'.format(tag, len(illustrations)))
    for illustration in illustrations:
        download_by_illustration_id(save_directory, illustration.id)
    log.info('end download illust by tag: {}'.format(tag))


# 获取整数倍 2324 -> [2000, 3000]
def get_10_20(number: int):
    figure = 0
    remain = number
    while remain // 10 > 0:
        remain = remain // 10
        figure += 1
    return [remain * (10 ** figure), (remain + 1) * (10 ** figure)]


# 下载TOP收藏图片
def download_top():
    directory = r"result/illusts-2020"
    top_illusts = query_top_total_bookmarks(count=50000)
    log.info("download illusts top size: {}".format(len(top_illusts)))
    for top_illust in top_illusts:
        if top_illust['total_bookmarks'] > 15026:
            log.info('skip illust: {}'.format(top_illust['id']))
            continue
        log.info("begin download illust: {}".format(top_illust))
        download_by_illustration_id(directory, top_illust["id"], spilt_bookmark=False,
                                    skip_min_width=1000, skip_min_height=1000)
        log.info('end download illust: {}'.format(top_illust))


# 从文件中读取P站图片下载地址（每一行一个URL），并从P站下载
def download_from_url_files(url_file_path, save_directory):
    # 创建文件夹
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    pixiv_api = AppPixivAPI(**_REQUESTS_KWARGS)
    pixiv_api.auth(refresh_token=_REFRESH_TOKEN)
    url_list = read_file_as_list(url_file_path)
    log.info('begin download image, url size: ' + str(len(url_list)))
    index = 0
    for url in url_list:
        log.info('index: ' + str(index))
        download_task(pixiv_api, save_directory, url)
        index += 1


def download_task_by_illust_ids():
    save_directory = r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result\illusts-2020'
    illust_ids = [83955499, 78914920, 85204622, 86387545, 87833548, 86825654, 87844590]
    log.info('begin download illust by ids. lens: {}'.format(illust_ids))
    for illust_id in illust_ids:
        download_by_illustration_id(save_directory, illust_id, skip_download=False, split_r_18=False)
    log.info('end')


def download_task_by_user_id(user_id=None, illust_id=None, save_dir=None):
    # 通过插画id查询对应的用户id
    if illust_id is not None:
        illust: Illustration = session.query(Illustration).get(illust_id)
        if illust is not None:
            user_id = illust.user_id

    if is_download_user(user_id):
        log.warn('The user hase been download. user_id: {}'.format(user_id))
        return

    # 如果给定了文件夹，一般是补充该用户的插画
    if user_id is None and save_dir is not None:
        parse_user_id = get_illust_id(save_dir)
        if parse_user_id >= 0:
            user_id = parse_user_id
    else:
        # 新用户需要创建文件夹
        save_dir = os.path.join(r'.\result\by-user', str(user_id))
    download_by_user_id(save_dir, user_id, skip_download=False, skip_max_page_count=10, split_r_18=False)


if __name__ == '__main__':
    # download_by_pool()
    # download_top()
    # tag = '四宮かぐや'
    # download_by_tag(os.path.join(r'.\result\by-tag', tag), tag)
    # download_task_by_user_id(save_dir=r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result\favorite\立绘-无场景\395595-cadillac-清爽-白色背景-少女')
    # download_task_by_user_id(user_id=3452804)
    download_task_by_user_id(illust_id=61026511)


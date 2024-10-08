#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import sqlalchemy as sql
import pymysql
import warnings
from sqlalchemy.orm import sessionmaker, scoped_session

from u_base.u_log import logger as log
from spider.pixiv.arrange.file_util import get_illust_id
from spider.pixiv.pixiv_api import PixivError
from .entity import Illustration, IllustrationTag, IllustrationImage, PixivUser

engine = sql.create_engine('mysql+pymysql://uusama:uusama@localhost:3306/pixiv?charset=utf8mb4')
SessionLocal: sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

session = scoped_session(SessionLocal)

# 忽略掉mysql执行insert ignore时的警告信息
warnings.filterwarnings('ignore', category=pymysql.Warning)


def save_illustration(illust: dict) -> None:
    if not illust or 'id' not in illust or not illust.get('id'):
        raise PixivError('Illust is empty or valid.')
    if 'image_urls' not in illust:
        raise PixivError('Illust image is empty.')
    illustration = Illustration(id=illust.get('id'), title=illust.get('title'), type=illust.get('type'))
    # if session.query(Illustration).filter(Illustration.id == illustration.id).first() is not None:
    #     print("The illustration is exist. illust_id: " + str(illustration.id))
    #     return
    illustration.caption = illust.get('caption')
    illustration.restrict = illust.get('restrict')

    # user_info 信息
    user_info = illust.get('user')
    pixiv_user = PixivUser(id=user_info.get('id'), name=user_info.get('name'), account=user_info.get('account'))
    pixiv_user.is_followed = user_info.get('is_followed')
    illustration.user_id = user_info.get('id')

    # 首页图片链接地址
    illustration_image = save_illustration_image(illust, illustration)
    illustration.image_url_square_medium = illustration_image.get('image_url_square_medium', None)
    illustration.image_url_medium = illustration_image.get('image_url_medium', None)
    illustration.image_url_large = illustration_image.get('image_url_large', None)
    illustration.image_url_origin = illustration_image.get('image_url_origin', None)

    illustration.tools = json.dumps(illust.get('tools'), ensure_ascii=False)
    illustration.create_date = illust.get('create_date')
    illustration.page_count = illust.get('page_count')
    illustration.width = illust.get('width')
    illustration.height = illust.get('height')
    illustration.sanity_level = illust.get('sanity_level')
    illustration.x_restrict = illust.get('x_restrict')
    illustration.series = illust.get('series')
    if 'meta_single_page' in illust and 'original_image_url' in illust.get('meta_single_page'):
        illustration.image_url_meta_origin = illust.get('meta_single_page').get('original_image_url')
    illustration.total_view = illust.get('total_view')
    illustration.total_bookmarks = illust.get('total_bookmarks')
    illustration.is_bookmarked = illust.get('is_bookmarked')
    illustration.visible = illust.get('visible')
    illustration.is_muted = illust.get('is_muted')
    illustration.r_18 = illust.get('r_18', False)
    illustration.total_comments = illust.get('total_comments', 0)

    # 保存tag
    illust_tags = []
    if 'tags' in illust and len(illust.get('tags')):
        for tag in illust.get('tags'):
            illust_tag_info = {'user_id': user_info.get('id'), 'illust_id': illust.get('id'),
                               'name': tag.get('name'), 'translated_name': ''}
            illust_tag = session.execute(IllustrationTag.__table__.insert().prefix_with('IGNORE'), illust_tag_info)
            illust_tags.append(illust_tag)
    session.merge(illustration)
    session.merge(pixiv_user)
    session.commit()


def save_illustration_image(illust: dict, illustration: Illustration) -> dict:
    # 图片链接地址
    illustration_image = base_illustration_image(illustration)

    # 单页插画处理
    image_url_info = illust.get('image_urls')
    illustration_image['image_url_square_medium'] = image_url_info.get('square_medium')
    illustration_image['image_url_medium'] = image_url_info.get('medium')
    illustration_image['image_url_large'] = image_url_info.get('large', '')
    illustration_image['image_url_origin'] = ''
    if 'meta_single_page' in illust and 'original_image_url' in illust.get('meta_single_page'):
        illustration_image['image_url_origin'] = illust.get('meta_single_page').get('original_image_url', '')
        session.execute(IllustrationImage.__table__.insert().prefix_with('IGNORE'), illustration_image)
        session.commit()

    # 多页插画图片地址处理
    page_index = 0
    for meta_image_url in illust.get('meta_pages'):
        if 'image_urls' in meta_image_url:
            page_index += 1
            meta_image_url_info = meta_image_url.get('image_urls')
            meta_illustration_image = base_illustration_image(illustration)
            meta_illustration_image['page_index'] = page_index
            meta_illustration_image['image_url_square_medium'] = meta_image_url_info.get('square_medium', '')
            meta_illustration_image['image_url_medium'] = meta_image_url_info.get('medium', '')
            meta_illustration_image['image_url_large'] = meta_image_url_info.get('large', '')
            meta_illustration_image['image_url_origin'] = meta_image_url_info.get('original', '')
            session.execute(IllustrationImage.__table__.insert().prefix_with('IGNORE'), meta_illustration_image)
            session.commit()
    return illustration_image


def base_illustration_image(illustration: Illustration) -> dict:
    return {
        'user_id': illustration.user_id,
        'illust_id': illustration.id,
        'title': illustration.title,
        'page_index': 1
    }


def query_top_total_bookmarks(count=100000, min_id=1, min_total_bookmarks=5000) -> list:
    cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), r"cache\top_total_bookmarks-{}.json".format(min_id))
    if os.path.isfile(cache_file):
        return json.load(open(cache_file, encoding='utf-8'))
    results = session.query(Illustration.id, Illustration.user_id, Illustration.total_bookmarks)\
        .filter(Illustration.type == 'illust')\
        .filter(Illustration.id >= min_id)\
        .filter(Illustration.total_bookmarks >= min_total_bookmarks)\
        .order_by(Illustration.total_bookmarks.desc()).limit(count).all()
    results = [v._asdict() for v in results]
    json.dump(results, open(cache_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    return results


def query_by_user_id(user_id, min_total_bookmarks=5000) -> list:
    cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), r"cache\user-{}-top-{}-illusts.json"
                              .format(user_id, min_total_bookmarks))
    if os.path.isfile(cache_file):
        return json.load(open(cache_file, encoding='utf-8'))
    results = session.query(Illustration.id, Illustration.user_id, Illustration.total_bookmarks)\
        .filter(Illustration.user_id == user_id)\
        .filter(Illustration.total_bookmarks >= min_total_bookmarks)\
        .order_by(Illustration.total_bookmarks.desc()).all()
    results = [v._asdict() for v in results]
    json.dump(results, open(cache_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    return results


def get_illustration_by_id(illustration_id: int):
    return session.query(Illustration).get(illustration_id)


# 更新插图的标签
def update_illustration_tag(illust_id, tag):
    illustration: Illustration = session.query(Illustration).get(illust_id)
    if illustration is None:
        log.info('The illustration is not exist. illust_id: {}'.format(illust_id))
        return
    log.info('process illust_id: {}, set tag to: {} '.format(illust_id, tag))
    illustration.tag = tag
    session.commit()


# 更新用户标签
def update_user_tag(user_id, tag, replace=True):
    user: PixivUser = session.query(PixivUser).get(user_id)
    if user is None:
        log.info('The user is not exist. user_id: {}'.format(user_id))
        return
    if replace:
        log.info('process user_id: {}, set tag to: {} '.format(user_id, tag))
        user.tag = tag
        session.commit()
    else:
        log.info('the user({}) has tag({}) and do not change.'.format(user_id, user.tag))


def get_pixiv_user(user_id) -> PixivUser:
    return session.query(PixivUser).get(user_id)


def is_download_user(user_id) -> bool:
    user: PixivUser = get_pixiv_user(user_id)
    return user is not None and user.tag != ''


# 是否指定的illust_id，用来提取某一个用户或者某一批插画
def is_special_illust_ids(illust_path: str = None, **kwargs) -> bool:
    if not kwargs.get('user_id') and not kwargs.get('illust_id'):
        log.error('The user_id or illust_id is empty.')
        return False
    user_id = kwargs.get('user_id')
    cache_illust_ids_path = os.path.dirname(__file__)
    cache_illust_ids_path = os.path.join(cache_illust_ids_path, r'.\cache\\' + str(user_id) + '-illust-ids.json')
    if not os.path.isfile(cache_illust_ids_path):
        # 某个用户的illust_id
        illust_ids = session.query(Illustration).filter(Illustration.user_id == user_id)\
            .order_by(Illustration.total_bookmarks.desc()).all()
        illust_ids = [x.id for x in illust_ids]
        log.info('query user_id: {}, illust_ids_size: {}'.format(user_id, len(illust_ids)))
        json.dump(illust_ids, open(cache_illust_ids_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    else:
        illust_ids = json.load(open(cache_illust_ids_path, 'r', encoding='utf-8'))
    current_illust_id = get_illust_id(illust_path)
    return current_illust_id in illust_ids

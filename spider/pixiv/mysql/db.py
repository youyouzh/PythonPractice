#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker

from spider.pixiv.pixiv_api import PixivError
from .entity import Illustration, IllustrationTag, IllustrationImage, PixivUser

engine = sql.create_engine('mysql+pymysql://uusama:uusama@localhost:3306/pixiv?charset=utf8mb4')
session = sessionmaker(bind=engine)()


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


def query_top_total_bookmarks(count=100000) -> list:
    cache_file = "cache.json"
    if os.path.isfile(cache_file):
        return json.load(open(cache_file))
    results = session.query(Illustration.id, Illustration.total_bookmarks, Illustration.total_view)\
        .filter(Illustration.type == 'illust')\
        .order_by(Illustration.total_bookmarks.desc()).limit(count).all()
    result = [dict(zip(v.keys(), v)) for v in results]
    json.dump(result, open(cache_file, 'w'), ensure_ascii=False, indent=4)
    return result


def get_illustration(illustration_id: int) -> Illustration:
    return session.query(Illustration).get(illustration_id)


def get_illustration_image(illustration_id: int) -> [IllustrationImage]:
    return session.query(IllustrationImage).filter(IllustrationImage.illust_id == illustration_id).all()


def update_illustration_image(illustration_image: IllustrationImage):
    session.merge(illustration_image)
    session.commit()

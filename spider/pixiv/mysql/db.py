#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker

from spider.pixiv.pixiv_api import PixivError
from .entity import Illustration, IllustrationTag, PixivUser

engine = sql.create_engine('mysql+pymysql://uusama:uusama@localhost:3306/pixiv?charset=utf8mb4')
session = sessionmaker(bind=engine)()


def save_illustration(illust: dict):
    if not illust or 'id' not in illust or not illust.get('id'):
        raise PixivError('Illust is empty or valid.')
    if 'image_urls' not in illust:
        raise PixivError('Illust image is empty.')
    illustration = Illustration(id=illust.get('id'), title=illust.get('title'), type=illust.get('type'))
    illustration.caption = illust.get('caption')
    illustration.restrict = illust.get('restrict')

    # user_info 信息
    user_info = illust.get('user')
    pixiv_user = PixivUser(id=user_info.get('id'), name=user_info.get('name'), account=user_info.get('account'))
    pixiv_user.is_followed = user_info.get('is_followed')
    illustration.user_id = user_info.get('id')

    # 图片链接地址
    image_url_info = illust.get('image_urls')
    illustration.image_url_square_medium = image_url_info.get('square_medium')
    illustration.image_url_medium = image_url_info.get('medium')
    illustration.image_url_large = image_url_info.get('large')
    illustration.image_url_origin = image_url_info.get('origin', '')
    if 'meta_single_page' in illust and 'original_image_url' in illust.get('meta_single_page'):
        illustration.image_url_meta_origin = illust.get('meta_single_page').get('original_image_url')

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
                               'name': tag.get('name'), 'translated_name': tag.get('translated_name', '')}
            illust_tag = session.execute(IllustrationTag.__table__.insert().prefix_with('IGNORE'), illust_tag_info)
            illust_tags.append(illust_tag)
    session.merge(illustration)
    session.merge(pixiv_user)
    session.commit()


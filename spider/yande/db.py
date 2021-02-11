# coding: utf-8
import sqlalchemy as sql
import os

from sqlalchemy import Column, Date, Index, String, TIMESTAMP, Text, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from u_base import u_log
from u_base import u_file

BaseModel = declarative_base()
metadata = BaseModel.metadata

engine = sql.create_engine('mysql+pymysql://uusama:uusama@localhost:3306/yande?charset=utf8mb4')
session = sessionmaker(bind=engine)()


# 插画表
class Post(BaseModel):
    __tablename__ = 'post'

    id = Column(BIGINT(20), primary_key=True)
    tags = Column(String(700), nullable=False, server_default=text("''"))
    author = Column(String(255), nullable=False, server_default=text("''"))
    source = Column(String(500), nullable=False, server_default=text("''"))
    score = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    md5 = Column(String(64), nullable=False, server_default=text("''"))
    file_size = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    sample_file_size = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    jpeg_file_size = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    file_ext = Column(String(16), nullable=False, server_default=text("''"))
    file_url = Column(String(255), nullable=False, server_default=text("''"))
    preview_url = Column(String(1000), nullable=False, server_default=text("''"))
    sample_url = Column(String(1000), nullable=False, server_default=text("''"))
    jpeg_url = Column(String(1000), nullable=False, server_default=text("''"))
    preview_width = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    preview_height = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    actual_preview_width = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    actual_preview_height = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    sample_width = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    sample_height = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    jpeg_width = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    jpeg_height = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    width = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    height = Column(INTEGER(1), nullable=False, server_default=text("'0'"))
    status = Column(String(32), nullable=False, server_default=text("''"))
    rating = Column(String(32), nullable=False, server_default=text("''"))
    mark = Column(String(64))
    parent_id = Column(INTEGER(1))
    has_children = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


def save_post(post_info):
    if not post_info or 'id' not in post_info or not post_info.get('id'):
        u_log.warn('post_info format is error: {}'.format(post_info))
        return None

    if session.query(Post).filter(Post.id == post_info.get('id')).first() is not None:
        u_log.info("The illustration is exist. illust_id: {}".format(post_info.get('id')))
        return None

    post = Post(id=post_info.get('id'), tags=post_info.get('tags')[:700])
    post.author = post_info.get('author')
    post.source = post_info.get('source')[:500]
    post.score = post_info.get('score')
    post.md5 = post_info.get('md5')
    post.file_size = post_info.get('file_size')
    post.sample_file_size = post_info.get('sample_file_size')
    post.jpeg_file_size = post_info.get('jpeg_file_size')
    post.file_ext = post_info.get('file_ext')
    post.file_url = post_info.get('file_url')
    post.preview_url = post_info.get('preview_url')
    post.sample_url = post_info.get('sample_url')
    post.jpeg_url = post_info.get('jpeg_url')
    post.preview_width = post_info.get('preview_width')
    post.preview_height = post_info.get('preview_height')
    post.actual_preview_width = post_info.get('actual_preview_width')
    post.actual_preview_height = post_info.get('actual_preview_height')
    post.sample_width = post_info.get('sample_width')
    post.sample_height = post_info.get('sample_height')
    post.jpeg_width = post_info.get('jpeg_width')
    post.jpeg_height = post_info.get('jpeg_height')
    post.width = post_info.get('width')
    post.height = post_info.get('height')
    post.status = post_info.get('status')
    post.rating = post_info.get('rating')
    post.parent_id = post_info.get('parent_id')
    post.has_children = post_info.get('has_children')
    session.merge(post)
    session.commit()


def query_post(post_id):
    return session.query(Post).get(post_id)


def mark_post(post, mark):
    post.mark = mark
    session.merge(post)
    session.commit()


def query_top_score_posts(count=1000) -> list:
    cache_file = r"cache\top_score_posts.json"
    if os.path.isfile(cache_file):
        return u_file.load_json_from_file(cache_file)
    results = session.query(Post.id, Post.score)\
        .order_by(Post.score.desc()).limit(count).all()
    result = [dict(zip(v.keys(), v)) for v in results]
    u_file.cache_json(result, cache_file)
    return result

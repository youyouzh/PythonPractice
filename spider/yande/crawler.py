# _*_coding:utf-8_*_
import requests

from u_base import u_file
from u_base import u_log
from db import save_post


CRAWL_URLS = {
    'post': 'https://yande.in/post.json'
}


def get_post_info() -> list:
    params = {
        'page': 1,
        'limit': 100
    }
    posts = u_file.get_json(CRAWL_URLS.get('post'), params)
    if not isinstance(posts, list):
        u_log.warn("The response is not post list.")
        return []
    u_log.info('post size: {}'.format(len(posts)))
    for post in posts:
        save_post(post)
        u_log.info('save post success. post_id: {}'.format(post.get('id')))
    return posts


if __name__ == '__main__':
    get_post_info()

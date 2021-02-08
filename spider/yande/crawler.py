# _*_coding:utf-8_*_
import requests

from u_base import u_file
from u_base import u_log
from db import save_post


CRAWL_URLS = {
    'post': 'https://yande.in/post.json'
}


def get_post_info():
    params = {
        'page': 1,
        'limit': 100
    }
    post_infos = u_file.get_json(CRAWL_URLS.get('post'), params)
    u_log.info('post size: {}'.format(len(post_infos)))
    for post_info in post_infos:
        save_post(post_info)
        u_log.info('save post success. post_id: {}'.format(post_info.get('id')))
    return post_info


if __name__ == '__main__':
    get_post_info()

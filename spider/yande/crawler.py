# _*_coding:utf-8_*_
import requests

from u_base import u_file
from u_base import u_log
from db import save_post, query_top_score_posts, mark_post, query_post, query_posts_by_tag


CRAWL_URLS = {
    'post': 'https://yande.in/post.json'
}
# crease
# screening
# fixme
# jpeg_artifacts
# /erect_nipples wet_clothes
# /wedding_dress wet_clothes
# paper texture
# /yukata no_bra open_shirt
# eyepatch
# dakimakura
# sex
# pubic_hair
# /tinkle
# binding_discoloration
# signed
# topless
# fellatio


def get_post_info(page) -> list:
    params = {
        'page': page,
        'limit': 100,
        # 'tags': 'chintora0201'
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


def crawl_post():
    max_page = 10000
    begin_page = 4155
    # -- not tags page:2927,  open_shirt 285
    while begin_page < max_page:
        u_log.info('-->begin crawl page: {}'.format(begin_page))
        posts = get_post_info(begin_page)
        if len(posts) == 0:
            u_log.info('all page have been crawled.')
            return
        u_log.info('-->end crawl page: {}, count: {}'.format(begin_page, len(posts)))
        begin_page += 1


def download_top():
    posts = query_top_score_posts(10000)
    directory = r'result'
    for post in posts:
        post = query_post(post.get('id'))
        if post.mark == 'downloaded':
            u_log.info('the post has been downloaded. id: {}'.format(post.id))
            continue
        u_log.info('begin download post. id: {}, score: {}, size: {}'.format(post.id, post.score, post.file_size))
        file_name = u_file.get_file_name_from_url(post.file_url)
        u_file.download_file(post.file_url, file_name, directory)
        mark_post(post, 'downloaded')


def download_tag():
    tag = 'fellatio'
    posts = query_posts_by_tag(tag)
    directory = r'result' + '\\' + tag
    for post in posts:
        post = query_post(post.get('id'))
        if post.mark == 'downloaded':
            u_log.info('the post has been downloaded. id: {}'.format(post.id))
            continue
        if post.score < 30:
            u_log.info('the post score is low. id: {}, score: {}'.format(post.id, post.score))
            continue
        u_log.info('begin download post. id: {}, score: {}, size: {}'.format(post.id, post.score, post.file_size))
        file_name = u_file.get_file_name_from_url(post.file_url)
        u_file.download_file(post.file_url, file_name, directory)
        mark_post(post, 'downloaded')


if __name__ == '__main__':
    download_tag()

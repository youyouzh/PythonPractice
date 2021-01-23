# -*- coding': 'utf-8 -*-
import requests
import time
import os
import json

from u_base import u_log
from u_base import u_file


URL = {
    'album': 'http://mobile.ximalaya.com/mobile-album/album/page/ts-1611290111252',
    'track_info': 'http://mobile.ximalaya.com/mobile/track/v2/baseInfo/1611290839498',
    'track_intro': 'http://mobile.ximalaya.com/mobile-track/richIntro'
}

HEADERS = {
    'user-agent': 'ting_7.3.3(SM-G9500,Android28)'
}


# 裁剪右边的秒数
CLIP_INFO = {
    '合集From everywhere 1日目': '15:30',
    '合集From everywhere 2日目': '19:11',
    '合集From everywhere 3日目': '7:50',
    '合集From everywhere 4日目': '08:03',
    '合集From everywhere 5日目': '11:24',
    '合集From everywhere 6日目': '05:50',
    '合集From everywhere 7日目': '13:65',
    '合集From everywhere 8日目': '03:48',
    '合集From everywhere 9日目': '18:35',
    '合集From everywhere 10日目': '16:20',
    '合集From everywhere 11日目': '09:30',
    '合集From everywhere 12日目': '13:34',
    '合集From everywhere 13日目': '18:04'
}


def get_album_track_info_page(album_id, page_id, page_size=20) -> dict:
    page_param = {
        'ac': 'WIFI',
        'albumId': album_id,
        'device': 'android',
        'isAsc': 'false',
        'isQueryInvitationBrand': 'true',
        'isVideoAsc': 'true',
        'pageId': page_id,
        'pageSize': page_size,
        'pre_page': '0',
        'source': '2',
        'supportWebp': 'true'
    }
    response = requests.get(URL['album'], params=page_param, headers=HEADERS)
    album_info: dict = json.loads(response.text)
    if album_info.get('ret') != 0 or 'data' not in album_info or 'tracks' not in album_info.get('data') \
            or 'list' not in album_info.get('data').get('tracks'):
        u_log.warn('The response is not contains tracks. {}'.format(response.text))
        return {}
    u_log.info('get track infos success, album_id: {}'.format(album_id))
    track_info = album_info.get('data').get('tracks')
    u_log.info('tracks total count: {}'.format(track_info.get('totalCount')))
    return track_info


def get_album_tracks(album_id) -> list:
    page_id = 1
    max_page = 2
    page_size = 130

    base_track_infos: list = []
    while page_id < max_page:
        track_info = get_album_track_info_page(album_id, page_id, page_size)
        if 'maxPageId' not in track_info:
            u_log.warn('The maxPageId is not exist. unknown response.')
            break

        for track in track_info.get('list'):
            base_track_infos.append({
                'trackId': track.get('trackId'),
                'title': track.get('title'),
                'duration': track.get('duration')
            })
        # max_page = track_info.get('maxPageId')
        page_id += 1
    u_log.info('track size: {}'.format(len(base_track_infos)))
    return base_track_infos


def get_track_info(track_id) -> dict:
    track_param = {
        'device': 'android',
        'trackId': track_id
    }
    response = requests.get(URL['track_info'], params=track_param, headers=HEADERS)
    u_log.info('get track info success. trackId: {}'.format(track_id))
    track_info: dict = json.loads(response.text)
    if track_info.get('ret') != 0 or 'trackInfo' not in track_info:
        u_log.warn('The response is not contains trackInfo. {}'.format(response.text))
        return {}
    track_info = track_info.get('trackInfo')

    intro_param = {
        'ac': 'WIFI',
        'device': 'android',
        'supportWebp': 'true',
        'trackId': track_id,
        'trackUid': 29200911
    }
    response = requests.get(URL['track_intro'], params=intro_param, headers=HEADERS)
    u_log.info('get track rich intro info success. trackId: {}'.format(track_id))
    track_intro_info = json.loads(response.text)
    if track_intro_info.get('ret') != 0 or 'richIntro' not in track_intro_info:
        u_log.warn('The response is not contains richIntro. {}'.format(response.text))
        return track_info
    track_info['richIntro'] = track_intro_info.get('richIntro')
    u_log.info('get all track info success. trackId: {}'.format(track_id))
    return track_info

    # return {
    #     'trackId': track_info.get('trackId'),
    #     'title': track_info.get('title'),
    #     'albumId': track_info.get('albumId'),
    #     'albumTitle': track_info.get('albumTitle'),
    #     'downloadAacSize': track_info.get('downloadAacSize'),
    #     'downloadAacUrl': track_info.get('downloadAacUrl'),
    #     'downloadSize': track_info.get('downloadSize'),
    #     'downloadUrl': track_info.get('downloadUrl'),
    #     'duration': track_info.get('duration'),
    #     'playPathAacv164': track_info.get('playPathAacv164'),
    #     'playPathAacv164Size': track_info.get('playPathAacv164Size'),
    #     'playPathAacv224': track_info.get('playPathAacv224'),
    #     'playPathAacv224Size': track_info.get('playPathAacv224Size'),
    #     'playUrl32': track_info.get('playUrl32'),
    #     'playUrl32Size': track_info.get('playUrl32Size'),
    #     'playUrl64': track_info.get('playUrl64'),
    #     'playUrl64Size': track_info.get('playUrl64Size'),
    #     'playHqSize': track_info.get('playHqSize'),
    #     'playPathHq': track_info.get('playPathHq'),
    #     'playtimes': track_info.get('playtimes'),
    #     'richIntro': track_intro_info.get('richIntro')
    # }


def get_album_track_info_from_cache(album_id) -> list:
    track_cache_file = r'cache\album-tracks-' + str(album_id) + '.json'
    if os.path.isfile(track_cache_file):
        u_log.info('use track info from cache file: {}'.format(track_cache_file))
        return u_file.load_json_from_file(track_cache_file)

    track_index = 1
    tracks: list = get_album_tracks(album_id)
    u_log.info('get_album_tracks return track size: {}'.format(len(tracks)))

    track_infos = []
    for track in tracks:
        track_infos.append(get_track_info(track.get('trackId')))
        u_log.info('end get track info: {}({}/{})'.format(track.get('trackId'), track_index, len(tracks)))
        track_index += 1
    u_log.info('all track infos size: {}'.format(len(track_infos)))
    u_file.cache_json(track_infos)
    return track_infos


def download_track():
    target_album_id = 4815905
    track_infos = get_album_track_info_from_cache(target_album_id)

    download_file_path = r'result'
    for track_info in track_infos:
        if track_info.get('title').find('坂本真绫') < 0:
            u_log.info('The track is not need. title: {}'.format(track_info.get('title')))
            continue
        if track_info.get('title').find('合集') >= 0:
            u_log.info('The track is collection. title: {}'.format(track_info.get('title')))
            continue
        file_name = str(track_info.get('trackId')) + '-' + track_info.get('title')
        # u_file.download_file(track_info.get('playUrl64'), file_name, download_file_path)
        u_log.info('download finish. trackId: {}, file_name: {}'.format(track_info.get('trackId'), file_name))


def build_content_html():
    target_album_id = 4815905
    track_infos = get_album_track_info_from_cache(target_album_id)
    template_content = u_file.get_content(r'cache\template.html')

    content = ''
    for track_info in track_infos:
        if track_info.get('title').find('坂本真绫') < 0:
            u_log.info('The track is not need. title: {}'.format(track_info.get('title')))
            continue
        if track_info.get('title').find('合集') >= 0:
            u_log.info('The track is collection. title: {}'.format(track_info.get('title')))
            continue
        content += '\n\n<h2>' + track_info.get('title') + '</h2>\n\n'
        content += track_info.get('richIntro')
    template_content.replace('{content}', content)
    u_file.write_content(r'cache\target.html', content)


if __name__ == '__main__':
    build_content_html()




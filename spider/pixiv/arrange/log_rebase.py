#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from spider.pixiv.arrange.file_util import read_file_as_list
import u_base.u_log as log


if __name__ == '__main__':
    log_file_path = r'./log/move-file.log'
    lines = read_file_as_list(log_file_path)
    log.info('The log file lines: {}'.format(len(lines)))
    for line in lines:
        line = line[80:]
        paths = line.split(' ---> ')
        source_path = paths[0]
        source_path = source_path.replace('collect', 'collect-2')

        target_path = paths[1][4:]
        target_path = target_path.replace(r'collect\small-2', r'illusts\small')
        if not os.path.isfile(target_path):
            log.info('The file is not find: {}'.format(target_path))
            continue

        log.info('rebase file: {}'.format(target_path))
        if not os.path.isdir(os.path.dirname(source_path)):
            os.makedirs(os.path.dirname(source_path))
        os.replace(target_path, source_path)

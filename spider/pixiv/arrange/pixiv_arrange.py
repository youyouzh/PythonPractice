#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from spider.pixiv.mysql.db import session, Illustration, IllustrationTag


# 更新本地整理好的插图
def arrange():
    # 目标文件夹
    directory = r"result\collect\初音未来"
    score = 5   # 分数， 8：有用的教程，7：一级棒， 7：很棒， 5：还可以，4：有点色色，3：无感，2：不管了，1：什么鬼不要
    if not os.path.exists(directory):
        print('The directory is not exist. ' + directory)
        return
    file_names = os.listdir(directory)
    for file_name in file_names:
        # 获取目录或者文件的路径
        if os.path.isdir(os.path.join(directory, file_name)):
            continue
        print('process file: ' + file_name)
        # 提取 illust_id
        illust_id = file_name.split('_')[0]
        if not illust_id.isnumeric():
            continue
        illustration: Illustration = session.query(Illustration).get(int(illust_id))
        if illustration is None:
            print('The illustration is not exist. illust_id: ' + illust_id)
            continue
        if illustration.score > 0:
            print("The illustration is exist. score: " + str(illustration.score))
            continue
        print('process illust_id: %s, set score to: %d ' % (illust_id, score))
        illustration.score = score
        session.commit()


# 移动、统一、分类文件
def collect_illusts():
    base_directory = r"result\illusts"
    illust_directories = ['10000-20000', '100000-200000', '20000-30000', '200000-300000', '30000-40000',
                          '300000-400000', '40000-50000', '5000-6000', '50000-60000', '6000-7000', '60000-70000',
                          '7000-8000', '70000-80000', '8000-9000', '80000-90000', '9000-10000', '90000-100000']
    move_target_directory = r"result\collect\wlop"
    move_tags = ['wlop', 'wlop']
    if not os.path.exists(move_target_directory):
        print('The directory is not exist. create: ' + move_target_directory)
        os.makedirs(move_target_directory)
    is_move_file = False
    move_file_count = 0
    for illust_directory in illust_directories:
        illust_directory = base_directory + '\\' + illust_directory
        illust_files = os.listdir(illust_directory)
        print('illust files size: %d' % len(illust_files))
        for illust_file in illust_files:
            full_source_illust_file_path = os.path.join(illust_directory, illust_file)       # 完整的源图片路径
            full_target_illust_file_path = os.path.join(move_target_directory, illust_file)  # 移动目标路径
            tags = illust_file.split('-')   # 从文件名分解得出包含的标签
            for tag in tags:
                for move_tag in move_tags:
                    if tag.find(move_tag) >= 0:
                        is_move_file = True
            if is_move_file:
                is_move_file = False
                move_file_count += 1
                print('find move file(%d): %s' % (move_file_count, full_source_illust_file_path))
                os.replace(full_source_illust_file_path, full_target_illust_file_path)
    print('----> total move file count: %d' % move_file_count)


if __name__ == '__main__':
    collect_illusts()
    # arrange()

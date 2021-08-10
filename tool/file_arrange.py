"""
文件整理相关工具
"""
# sudo apt-get install python-libtorrent
# !/usr/bin/env python

import os
import re
import u_base.u_file as u_file
import u_base.u_log as log
from urllib.parse import unquote


def refactor_test_file(main_dir):
    """
    重构测试文件，for Java，根据main文件夹下的类，通过测试文件规则，找到相对应目录下的测试文件，进行移动
    :param main_dir: 源代码文件夹
    """
    main_files = u_file.get_all_sub_files_with_cache(main_dir)
    for main_file in main_files:
        main_file_path = os.path.split(main_file)[0]
        main_filename = os.path.split(main_file)[1]

        test_file_path = main_file_path.replace('athena-learning', 'athena-web')
        test_file_path = test_file_path.replace('main', 'test')

        # 检查测试文件是否存在
        predict_test_file = os.path.join(test_file_path, 'IT' + main_filename)
        if os.path.isfile(predict_test_file):
            move_test_file(predict_test_file, main_file_path, main_filename)

        predict_test_file = os.path.join(test_file_path, 'Test' + main_filename)
        if os.path.isfile(predict_test_file):
            move_test_file(predict_test_file, main_file_path, main_filename)

        predict_test_file = os.path.join(test_file_path, main_filename.replace('.java', 'Test.java'))
        if os.path.isfile(predict_test_file):
            move_test_file(predict_test_file, main_file_path, main_filename)


def move_test_file(predict_test_file, main_file_path, main_filename):
    """
    移动测试文件
    :param predict_test_file: 测试文件
    :param main_file_path: main文件夹路径
    :param main_filename: main下的class文件名
    :return:
    """
    move_target_test_path = main_file_path.replace('main', 'test')
    move_target_test_path = os.path.join(move_target_test_path, main_filename.replace('.java', 'Test.java'))
    log.info('The test file is exist. move {} -> {}'.format(predict_test_file, move_target_test_path))

    # 移动文件
    u_file.ready_dir(move_target_test_path)
    os.replace(predict_test_file, move_target_test_path)

    # 修改类中的类名
    handler = open(move_target_test_path, 'r+', encoding='UTF-8')
    content = handler.read()
    handler.seek(0)
    handler.write(content.replace(os.path.split(predict_test_file)[1].split('.')[0],
                                  main_filename.replace('.java', 'Test')))
    handler.close()


def modify_picture_suffix(source_directory):
    """
    批量修改图片后缀名，垃圾微信报错GIF图片有问题
    :param source_directory: 需要处理的文件夹路径
    :return:
    """
    sub_file_paths = u_file.get_all_sub_files(source_directory)
    min_gif_picture_size = 500 * 1024
    for sub_file_path in sub_file_paths:
        if os.path.isdir(sub_file_path):
            log.info('The file is directory: {}'.format(sub_file_path))
            continue
        if os.path.getsize(sub_file_path) < min_gif_picture_size:
            log.info('The file size is small. file: {}, size: {}'.format(sub_file_path, os.path.getsize(sub_file_path)))
            continue
        sub_file_name = os.path.split(sub_file_path)[1]
        sub_file_name_suffix = os.path.splitext(sub_file_name)[1]

        move_target_file_path = sub_file_path.replace(sub_file_name_suffix, ".gif")
        log.info('move file: {} --> file: {}'.format(sub_file_path, move_target_file_path))
        os.replace(sub_file_path, move_target_file_path)


def collect_sub_files(source_root_directory, move_target_directory):
    """
    遍历所有子文件，然后移动到另一个地方，避免有些下载的文件嵌套太深
    可以批量把某个文件夹下的所有文件移动到指定的目录下
    :param source_root_directory: 检查的路径
    :param move_target_directory: 统一移动到的路径
    :return:
    """
    if not os.path.isdir(move_target_directory):
        # 文件不存在则创建
        os.makedirs(move_target_directory)
    sub_file_paths = u_file.get_all_sub_files(source_root_directory)

    for sub_file_path in sub_file_paths:
        if os.path.isdir(sub_file_path):
            log.info('The file is directory: {}'.format(sub_file_path))
            continue
        sub_file_name = os.path.split(sub_file_path)[1]
        sub_file_name_suffix = os.path.splitext(sub_file_name)[1]
        if sub_file_name_suffix != '.jpg' and sub_file_name_suffix != '.hdr':
            log.info('The file is not hdr file: {}'.format(sub_file_name))
            continue

        move_target_file_path = os.path.join(move_target_directory, sub_file_name)
        if os.path.isfile(move_target_file_path):
            log.warn('The move target file is exist: {}'.format(move_target_file_path))
            continue

        log.info('move file: {} --> file: {}'.format(sub_file_path, move_target_file_path))
        os.replace(sub_file_path, move_target_file_path)


def replace_file_name(source_root_directory, replace_ad_str):
    """
    一般用来去掉下载文件中的广告
    :param replace_ad_str: 需要替换掉的广告文字
    :param source_root_directory: 处理的文件夹
    :return:
    """
    sub_file_paths = u_file.get_all_sub_files(source_root_directory)

    for sub_file_path in sub_file_paths:
        move_target_file_path = sub_file_path.replace(replace_ad_str, '')
        if os.path.isfile(move_target_file_path):
            log.warn('The target file is exist: {}'.format(move_target_file_path))
            continue

        log.info('rename file: {} --> file: {}'.format(sub_file_path, move_target_file_path))
        os.replace(sub_file_path, move_target_file_path)


def replace_file_content(file_path):
    """
    替换知乎中的中转链接
    :param file_path: 替换的文件路径
    :return:
    """
    file_content = u_file.read_content(file_path)
    # text = '<a href="https://link.zhihu.com/?target=http%3A//index.iresearch.com.cn/pc" class=" wrap external">'
    replace_content = re.sub(r'href="[^"]+"',
                             lambda match: unquote(match.group(0).replace('https://link.zhihu.com/?target=', '')),
                             file_content)
    u_file.write_content(r'D:\forme\Git_Projects\python-base\tool\industry-analysis-'
                         r'report-replace.html', replace_content)


def generate_gitbook_summary(source_dir):
    """
    生成gitbook的summary目录文件，通过遍历文件目录树实现
    :param source_dir: source_dir
    :return:
    """
    sub_file_paths = u_file.get_all_sub_files(source_dir, contain_dir=True)
    summary_content = ''
    sub_file_paths.sort()
    exclude_paths = ['.git', '.idea', 'assets', 'temp', 'node_modules', '_book']
    for sub_file_path in sub_file_paths:
        relative_path = sub_file_path.replace(source_dir + '\\', '')
        # 过滤掉非markdown文件
        ignore = False
        for exclude_path in exclude_paths:
            if sub_file_path.find(exclude_path) >= 0:
                ignore = True
        if ignore:
            continue

        path_depth = relative_path.count('\\')
        menu = '  ' * path_depth

        if os.path.isfile(sub_file_path):
            if sub_file_path.find('.md') >= 0:
                menu += '- [{}]({})'.format(os.path.split(relative_path)[1].replace('.md', ''), relative_path)
            else:
                continue
        else:
            menu += '- {}'.format(relative_path.split('\\')[-1])
        summary_content += menu + "\n"
    u_file.write_content(r'cache\result.md', summary_content)
    print(summary_content)


if __name__ == "__main__":
    modify_picture_suffix(r'D:\WeiXin')

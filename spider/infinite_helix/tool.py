"""
Dota2游戏RPG地图，无限螺旋解包数据处理相关工具
解包使用 gcfscape，解密使用VRF： https://github.com/SteamDatabase/ValveResourceFormat
"""
import os
import re

import u_base.u_file as u_file
import u_base.u_log as log


# 解析常量表： panorama/localization/addon_schinese.txt
def extract_constants() -> dict:
    constant_kvs = u_file.read_file_as_list(r'data/text.txt')
    constants = {}
    for constant_kv in constant_kvs:
        kvs = str(constant_kv).replace('\t', '').split('""')
        if len(kvs) < 2:
            # log.info('unknown format text: {}'.format(line))
            continue
        key = kvs[0].replace('"', '')
        value = kvs[1].replace('"', '')
        constants[key] = value
    return constants


# 反编译V社编译后的资源
def decompile_file(input_file, output_file=None):
    decompile_ext_map = {
        '.vtex_c': '.png',
        '.vxml_c': 'xml'
    }
    if not os.path.isfile(input_file):
        log.error('The file is not exist. path: {}'.format(input_file))
        return output_file
    file_meta = u_file.get_file_meta(input_file)
    suffix = file_meta['suffix']
    if suffix not in decompile_ext_map:
        log.warn('Do not define the suffix map. path: {}'.format(input_file))
        return output_file

    if not output_file:
        output_file = str(input_file).replace(suffix, decompile_ext_map.get(suffix))

    compile_exe_path = r'data\plugins\Decompiler.exe'
    compile_exe_path = os.path.abspath(compile_exe_path)
    command = compile_exe_path + ' -d -i "' + input_file + '" -o "' + output_file + '"'
    log.info('command: {}'.format(command))
    os.system(command)


# 物品图标提取
def extract_item_images():
    items = extract_item_meta()
    item_dir = r'D:\Program Files (x86)\Steam\steamapps\workshop\content\570\2817343725\root\panorama\images\items\custom'
    for item_file in os.listdir(item_dir):
        full_item_file = os.path.join(item_dir, item_file)
        if 'vtex_c' not in item_file:
            continue

        file_info = u_file.get_file_meta(full_item_file)
        id = 'item_' + file_info['filename'].replace('_png', '')
        if id not in items:
            log.warn('The item id is not exist. id: {}'.format(id))
            output_file = os.path.join(r'data\items', file_info['filename'].replace('_png', '') + '.png')
            continue
        else:
            output_file = os.path.join(r'data\items', file_info['filename'].replace('_png', '') + '_' + items[id]['name'] + '.png')
        if os.path.isfile(output_file):
            log.info('The decompile file is exist: {}'.format(output_file))
            continue
        decompile_file(full_item_file, output_file)


# 探索事件选项表提取
def output_explore_quest():
    explore_dungeons = []
    constants = extract_constants()
    for (name, desc) in constants.items():
        if 'explore_dungeon_event' not in name:
            continue

        explore_dungeons.append(name.replace('selection_', '') + ': ' + desc)

    explore_dungeons.sort()
    output = ''
    for content in explore_dungeons:
        if 'A' not in content and 'B' not in content and 'C' not in content and 'D' not in content and 'result' not in content:
            output += "\n\n"

        content = re.compile('explore_dungeon_event_\\d+_[ABCDE]: +').sub('', content)  # 选项
        content = re.compile('explore_dungeon_event_\\d+_[ABCDE]_result: +').sub('', content)  # 单个结果
        content = re.compile('explore_dungeon_event_\\d+_[ABCDE]_result_(\\d+): +').sub('', content)  # 多个结果
        content = re.compile('explore_dungeon_event_').sub('', content)   # 题目
        output += content + "\n"
    u_file.write_content(r'data/explore.txt', output)


# 加载xml文件
def load_xml_json(path: str) -> dict:
    if not os.path.isfile(path):
        log.error('The file is not exist. file: {}'.format(path))
        return {}

    content = u_file.read_content(path)
    regex = re.compile(r"= (\{[\n '\w:\{,\}\[\]\"\.-]+);")
    result = regex.search(content).group(1)
    result = eval(result.replace('true', 'True'))
    return result


# 提取物品列表信息： /panorama/layout/custom_game/data/item_list.xml
def extract_item_meta():
    item_list_xml = r'data\item_list.xml'
    items = load_xml_json(item_list_xml)
    constants = extract_constants()
    for (name, desc) in constants.items():
        if 'DOTA_Tooltip_ability_item' not in name:
            continue
        id_regex = re.compile(r'DOTA_Tooltip_ability_(item_\d+)')
        id = id_regex.search(name).group(1)
        if id is None or id not in items:
            log.warn('The item is not config. name: {}, desc: {}'.format(name, desc))
            continue

        items[id]['key'] = id
        if '_Lore' in name:
            items[id]['lore'] = desc
        elif '_Description' in name:
            items[id]['desc'] = desc
        else:
            items[id]['name'] = desc

    attribute_map = u_file.load_json_from_file(r'data\attribute.json')

    cn_items = {}
    for (id, item) in items.items():
        cn_item = {}
        for (key, value) in item.items():
            if key in attribute_map:
                cn_item[attribute_map[key]] = value
            else:
                cn_item[key] = value
        cn_items[id] = cn_item

    u_file.dump_json_to_file(r'data\items.json', items)
    u_file.dump_json_to_file(r'data\cn_items.json', cn_items)
    return items


if __name__ == '__main__':
    extract_item_meta()
    # extract_item_images()
    output_explore_quest()

"""
戴森球计划相关工具
"""
import json
import os.path

from u_base import u_file
from u_base.u_log import logger

RECIPES_TEXT_FILEPATH = r'cache/recipes.txt'
RECIPES_JSON_FILEPATH = r'cache/recipes.json'


def process_recipes(use_cache: bool = True) -> list:
    """
    处理配方表，配方表参考网站: <https://numbercal.inscode.cc/>或者<http://quantifycalculator.com/>的配方管理表格复制
    :param use_cache: 是否使用缓存文件
    :return:
    """
    if use_cache and os.path.isfile(RECIPES_JSON_FILEPATH):
        logger.info('使用缓存文件')
        return json.load(open(RECIPES_JSON_FILEPATH, 'r'))
    text_recipes = u_file.read_file_as_list(RECIPES_TEXT_FILEPATH)
    recipe_infos = []
    for text_recipe in text_recipes:
        recipe_items = text_recipe.split('\t')
        recipe_info = {
            '名称': recipe_items[0].split('*')[1],
            '数量': float(recipe_items[0].split('*')[0]),
            '耗时': float(recipe_items[3].replace('s', '')),
        }

        # 解析物品列表
        def parse_items(items_text):
            item_infos = []
            for item in items_text.split('+'):
                if item.strip() == '':
                    continue
                item_info = {
                    '名称': item.split('*')[1].strip(),
                    '数量': float(item.split('*')[0]),
                }
                item_infos.append(item_info)
            return item_infos

        recipe_info['多余产物'] = parse_items(recipe_items[1])

        # 解析原料
        recipe_info['原料'] = parse_items(recipe_items[2])
        recipe_infos.append(recipe_info)
    # 将数据存入json文件
    u_file.dump_json_to_file(RECIPES_JSON_FILEPATH, recipe_infos)


# 计算给定物品材料
def cal_recipe_materials(items: list):
    recipes = process_recipes()
    total_materials = {}
    for recipe in recipes:
        if recipe['名称'] not in items:
            continue
        # 先计算一分钟能生产多少个
        per_min_count = recipe['数量'] * 60 / recipe['耗时']
        print(f'{recipe["名称"]}: {per_min_count}')
        # 汇总需要的材料
        for material in recipe['原料']:
            if material['名称'] not in total_materials:
                total_materials[material['名称']] = {
                    '名称': material['名称'],
                    '数量': material['数量'] * per_min_count,
                    '建筑数量': 1
                }
            else:
                total_materials[material['名称']]['数量'] += material['数量'] * per_min_count
                total_materials[material['名称']]['建筑数量'] += 1
    # 打印需要的材料
    print('-----------')
    total_materials = list(total_materials.values())
    total_materials.sort(key=lambda x: x['数量'], reverse=True)
    print(f'总计需要材料: {len(total_materials)}')
    for material in total_materials:
        print(f'{material}')


if __name__ == '__main__':
    process_recipes(False)
    cal_recipe_materials(['电弧熔炉', '风力涡轮机', '采矿机', '火力发电机', '电力感应塔', '矩阵研究站', '原油精炼厂', '化工厂', '地基', '抽水机', '制作台Mk.Ⅰ'])

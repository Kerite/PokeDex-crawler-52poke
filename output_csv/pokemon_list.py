# coding:utf-8
import csv
import re

from bs4 import BeautifulSoup

import pokemon_info
import utils
import value_map_dict

"""
映射地区形态的名称到枚举的键
"""
regional_variant_dic = {
    "": "NORMAL",
    "阿罗拉的样子": "ALOLA",
    "伽勒尔的样子": "GALAR",
    "洗翠的样子": "HISUIAN",
}
# 被忽略的地区形态
ignored_regional_variant = [
    "白条纹的样子"
]


def update_pokemon_list(start_dex_num: int):
    """
    更新宝可梦列表（从 宝可梦列表页面 抓取列表后遍历每只宝可梦并存到csv中）
    :param start_dex_num: 开始的宝可梦的图鉴序号
    :return:
    """
    style_url = "https://wiki.52poke.com/load.php?lang=zh-hans&modules=ext.gadget.msp"
    r = utils.request_get(style_url)
    styles = re.findall(r"\.(sprite-icon-[0-9a-zA-Z]*?)\{background-position:([\-0-9]*?)(px)? ([\-0-9]*?)(px)?}",
                        r.text)
    style_dict = {}
    for style in styles:
        style_dict[style[0]] = (abs(int(int(style[1]) / 68)), abs(int(int(style[3]) / 56)))

    print(style_dict)
    url = "https://wiki.52poke.com/zh-hans/pmlist"
    r = utils.request_get(url)
    soup = BeautifulSoup(r.text, features="html.parser")

    tables = soup.find_all("table", "eplist")
    with open('./output_csv/pokemon_list.csv', 'a', newline='', encoding='UTF-8') as csv_file:
        pokemon_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        generation = 1
        for pokemon_table in tables:
            pokemon_rows = pokemon_table.find_all('tr')
            for pokemon_row in pokemon_rows:
                tds = pokemon_row.find_all('td')
                if len(tds) > 0:
                    pokemon_sub_name = ""
                    if tds[2].small is not None:
                        pokemon_sub_name = tds[2].small.a.string
                    if pokemon_sub_name in ignored_regional_variant:
                        continue
                    pokemon_num = tds[0].string.replace('#', '').replace("\n", '')
                    if int(pokemon_num) < start_dex_num:
                        continue
                    pokemon_name = tds[2].a.string
                    pokemon_detail = pokemon_info.get_pokemon_info(pokemon_name)
                    pokemon_type1 = tds[5].a.string
                    pokemon_type2 = ''
                    pokemon_icon_style = tds[1].a.span.attrs['class'][1]
                    pokemon_icon_location = 0
                    pokemon_icon_location_x, pokemon_icon_location_y = (0, 0)
                    if pokemon_icon_style in style_dict:
                        pokemon_icon_location_x, pokemon_icon_location_y = style_dict[pokemon_icon_style]
                        pokemon_icon_location = pokemon_icon_location_y * 30 + pokemon_icon_location_x

                    if tds[6].a is not None:
                        pokemon_type2 = tds[6].a.string
                    print([
                        int(pokemon_num), pokemon_name, pokemon_sub_name, value_map_dict.pokemon_types[pokemon_type1],
                        value_map_dict.pokemon_types[pokemon_type2], generation, pokemon_icon_location_y,
                        pokemon_icon_location_x,
                        pokemon_icon_location
                    ])
                    pokemon_writer.writerow([
                        int(pokemon_num), pokemon_name, regional_variant_dic[pokemon_sub_name],
                        value_map_dict.pokemon_types[pokemon_type1], value_map_dict.pokemon_types[pokemon_type2],
                        generation,
                        pokemon_icon_location_y, pokemon_icon_location_x, pokemon_detail
                    ])
            generation = generation + 1


if __name__ == '__main__':
    update_pokemon_list(0)

import requests
from bs4 import BeautifulSoup
import re
import utils
import opencc

proxies = {
    'http': '127.0.0.1:7890',
    'https': '127.0.0.1:7890'
}
dex_generation_name_dic = {
    'redgreendex': '红绿',
    'bluedex': "蓝",
    'yellowdex': "皮卡丘",
    'golddex': '金',
    'silverdex': '银',
    'crystaldex': '水晶',
    'rubydex': "红宝石",
    'sapphiredex': '蓝宝石',
    'emeralddex': '绿宝石',
    'rsedex': '宝石',
    'firereddex': '火红',
    'leafgreendex': '叶绿',
    'frlgdex': '火红/叶绿',
    'pearldex': '珍珠',
    'diamonddex': '钻石',
    'platinumdex': '白金',
    'dpdex': '珍珠/钻石',
    'dpptdex': '珍珠/钻石/白金',
    'heartgolddex': '心金',
    'soulsilverdex': '魂银',
    'hgssdex': '心金/魂银',
    'blackdex': '黑',
    'whitedex': '白',
    'bwdex': '黑/白',
    'b2w2dex': '黑2/白2',
    'sundex': '日',
    'moondex': '月',
    'ultrasundex': '究极太阳',
    'ultramoondex': '究极月亮',
    'xdex': 'X',
    'ydex': 'Y',
    'omegarubydex': '欧米伽红宝石',
    'alphasapphiredex': '阿尔法蓝宝石',
    'orasdex': '欧米伽红宝石/阿尔法蓝宝石',
    'letsgodex': "Let's Go! 皮卡丘'/Let's Go! 伊布",
    'Swdex': '剑',
    'Shdex': '盾',
    'bddex': '晶灿钻石',
    'spdex': '明亮珍珠',
    'bdspdex': '晶灿钻石/明亮珍珠',
    'ladex': '传说 阿尔宙斯'
}
week_dic = {
    '一': 1,
    '二': 2,
    '三': 3,
    '四': 4,
    '五': 5,
    '六': 6,
    '七': 7,
}
gen_letter_dic = {
    'D': '珍珠',
    'P': '钻石',
    'Pt': '白金',
    'BDSP': '晶灿钻石/明亮珍珠',
    'LA': '传说 阿尔宙斯',
    'SP': '明亮珍珠',
    'BD': '晶灿钻石',
    'RGBY': ""
}
species_strength_dic = {
    "HP": "hp", '攻击': 'atk', '防御': 'def', '特攻': 'spa', '特防': 'spd', '速度': 'speed', '特殊': 'spa'
}


def cave_replace(match):
    """
    替换洞穴的描述
    :param match:
    :return:
    """
    match_type = match.group(1)
    match_nums = match.group(2)
    if match_type == 'a':
        return "巢穴" + "（红色）" + match_nums.replace('|', ',')
    else:
        return "巢穴" + "（紫色）" + match_nums.replace('|', ',')


def get_pokemon_info(pokemon_name):
    """
    获取宝可梦信息（通过宝可梦名称）
    :param pokemon_name: 宝可梦的名字
    :return:
    """
    url = "https://wiki.52poke.com/index.php?title=" + pokemon_name + "&action=edit"
    r = utils.request_get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    source_code = soup.find("textarea", {'name': "wpTextbox1"}).string \
        .replace('	', '')
    converter = opencc.OpenCC()
    source_code = converter.convert(source_code)

    # 获取基本信息
    print("===基本信息===")
    dex_basic_info = {}
    # dex_basic_info_str = re.sub(r"{{[\S ]*}}", "", source_code)
    dex_basic_info_str = re.findall(r"{{宝可梦信息框[\S\n ]*?==", source_code)[0]
    # print("dex_basic_info_str", dex_basic_info_str)
    # print(dex_basic_info_str)
    dex_basic_infos = re.findall(r"\|(\S*?)=([\S \n]*?)\n", dex_basic_info_str)
    print('dex_basic_infos', dex_basic_infos)
    for dex_basic_info_item in dex_basic_infos:
        dex_basic_info[dex_basic_info_item[0]] = dex_basic_info_item[1].replace('\n', '')
    print(dex_basic_info)

    # 获取图鉴描述
    print("===宝可梦图鉴描述===")
    dex = re.findall(r"\{{2}图鉴[\s\S]*?\n}{2}", source_code)[0]
    dex_descriptions = re.findall(r"\|([a-zA-Z0-9]*)=((-\{zh-hans:(\S*?);)|((\S*?)\{{2}))", dex)
    # 最终结果
    pokemon_details_dex_description = {}
    for dex_description in dex_descriptions:
        print(dex_generation_name_dic[dex_description[0]], '3', dex_description[3], '5', dex_description[5])
        pokemon_details_dex_description[dex_description[0]] = dex_description[3]
    print(pokemon_details_dex_description)

    # 获得方式
    print("===获得方式===")
    spread_full_str: str = re.findall(r"===获得方式===[\s\S]*?===", source_code)[0]
    spread_full_str = re.sub(r"{{(?!分布)(?P<content>.[^{^}]*?)}}", match_first, spread_full_str)
    spread_full_str = re.sub(r"\[{2}(?P<content>.*?)]{2}", match_second, spread_full_str)
    spreads = re.findall(r"\{{2}分布/main[\s\S]*?}}\n", spread_full_str)
    # 最终结果
    pokemon_details_spread = []
    for spread in spreads:
        spread = spread.replace('\n', '')
        # spread_str = re.sub(r"{{(?!分布)(?P<content>.[^{^}]*?)}}", match_first, spread)
        # 替换物品/星期（不同描述需要改进）
        # spread_str = re.sub(r"{{([^\{\}\|]*)\|([^\{\}\|]*)}}", "\\2", spread)
        # 替换用[[]]框起来的内容
        # spread_str = re.sub(r"\[{2}(?P<content>.*?)]{2}", match_second, spread_str)
        print("spread_str", spread)
        # 替换巢穴信息
        # spread_str = re.sub(r"\{{2}巢穴\|([ap])\|([0-9|]*)}{2}", cave_replace, spread_str)
        # 替换 tt
        # spread_str = re.sub(r"{{tt\|\*\|([^{}]*)}}", "(\\1)", spread_str)
        # 替换
        # spread_str_grouped = re.findall(r"{{分布/main\|([0-9]*)\|([A-Z]*\|){5}([^|]*)\|([^|]*)\|([^|]*)\|[^|}]*}}", spread_str)
        spread_split = spread.split("|")
        print(spread_split)
        spread_location = spread_split[7].replace("\n", "")
        spread_path = spread_split[8]
        spread_note = ""
        if len(spread_split) >= 10:
            spread_note = spread_split[9].replace("}}", "").replace("\n", "")
        else:
            spread_path = spread_path.replace("}}", "")
        print("地点：", spread_location,
              "方式：", spread_path,
              "备注：", spread_note)
        pokemon_details_spread.append({
            'location': spread_location,
            'path': spread_path,
            'note': spread_note
        })
        print()
    print(pokemon_details_spread)

    # 匹配种族值
    print("===种族值===")
    full_species_strength_str = re.findall(r'===种族值===\n[\s\S]*?{[\s\S]*?===', source_code)
    print(full_species_strength_str)
    # 对于有多种形态的宝可梦（如原始回归，Mega形态）可能匹配出多个结果
    species_strength_titles = re.findall(r"title=\"([\S ]*?)\"[>\n{]{3}", full_species_strength_str[0])
    species_strength_strs = re.findall(r"\{{2}(?:种族值|種族值)[\s\S]*?}{2}", full_species_strength_str[0])
    print(species_strength_titles)
    # 最终结果
    pokemon_details_species_strength = []
    for idx, species_strength_str in enumerate(species_strength_strs):
        species_strengths = re.findall(r"(HP|攻击|防御|特攻|特防|速度|特殊)=([0-9]*)",
                                       species_strength_str.replace(' ', ''))
        # print(species_strengths)
        species_strength_info = {}
        for species_strength in species_strengths:
            species_strength_info[species_strength_dic[species_strength[0]]] = species_strength[1].replace('}}', '')
        pokemon_details_species_strength.append(species_strength_info)
        if len(species_strength_titles) > 0:
            species_strength_info['form_name'] = species_strength_titles[idx]
    print(pokemon_details_species_strength)

    return {
        'basic_info': dex_basic_info,
        'dex_description': pokemon_details_dex_description,
        'pokemon_spread': pokemon_details_spread,
        'pokemon_details_species_strength': pokemon_details_species_strength
    }


def match_first(matched: re.Match):
    matched_str = matched.group('content')
    # print("匹配到的格式信息：", matched_str)
    split_matched_str = matched_str.split('|')
    match split_matched_str[0]:
        case 'm':
            # 需要秘传技能
            return split_matched_str[1]
        case '形态变化':
            return split_matched_str[1] + '的样子'
        case 'sup/5':
            # 作品角标
            return ''
        case 'sup/6':
            # 作品角标
            return ''
        case 'pdw':
            return split_matched_str[1]
        case '道路':
            road_str = split_matched_str[1] + '('
            for road_str_index in range(2, len(split_matched_str)):
                road_str = road_str + split_matched_str[road_str_index] + ','
            return road_str.removesuffix(',') + ')'
        case 'female':
            return '♀'
        case 'male':
            return '♂'
        case 'Sup/W':
            # 天气
            return 'WEATHER(' + split_matched_str[1] + ')'
        case 'tt':
            print(split_matched_str)
            return '(' + split_matched_str[2] + ')'
        case _:
            return ""


def match_second(match: re.Match):
    matched_str = match.group('content')
    split_matched_strs = matched_str.split('|')
    return split_matched_strs[-1]


if __name__ == '__main__':
    # test_pokemon_names = ("波克基斯", "阿尔宙斯")
    # for test_pokemon_name in test_pokemon_names:
    #     get_pokemon_info(test_pokemon_name)
    while True:
        pokemon_name_input = input("输入宝可梦名称:")
        pokemon_info = get_pokemon_info(pokemon_name_input)
        print(pokemon_info)

import requests
from bs4 import BeautifulSoup
import re

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
    'rsedex': '宝石',
    'firereddex': '火红',
    'leafgreendex': '叶绿',
    'pearldex': '珍珠',
    'diamonddex': '钻石',
    'platinumdex': '白金',
    'dpdex': '珍珠/钻石',
    'dpptdex': '珍珠/钻石/白金',
    'heartgolddex': '心金',
    'soulsilverdex': '魂银',
    'hgssdex': '心金/魂银',
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
    'BD': '晶灿钻石'
}


def cave_replace(match):
    match_type = match.group(1)
    match_nums = match.group(2)
    if match_type == 'a':
        return "巢穴" + "（红色）" + match_nums.replace('|', ',')
    else:
        return "巢穴" + "（紫色）" + match_nums.replace('|', ',')


def get_pokemon_info(pokemon_name):
    url = "https://wiki.52poke.com/index.php?title=" + pokemon_name + "&action=edit"
    r = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(r.text, features="html.parser")
    source_code = soup.find("textarea", {'name': "wpTextbox1"}).string

    # 获取图鉴描述
    print("===宝可梦图鉴描述===")
    dex = re.findall(r"\{{2}图鉴[\s\S]*?\n}{2}", source_code)[0]
    dex_descriptions = re.findall(r"\|([a-zA-Z0-9]*)=((-\{zh-hans:(\S*?);)|((\S*?)\{{2}))", dex)
    for dex_description in dex_descriptions:
        print(dex_generation_name_dic[dex_description[0]], dex_description[3], dex_description[5])

    # 获得方式
    print("===获得方式===")
    spreads = re.findall(r"\{{2}分布/main.*?\n", source_code)
    for spread in spreads:
        # 替换物品/星期（不同描述需要改进）
        spread_str = re.sub(r"{{([^\{\}\|]*)\|([^\{\}\|]*)}}", "\\2", spread)
        # 替换用[[]]框起来的内容
        spread_str = re.sub(r"\[{2}(.*?)]{2}", "\\1", spread_str)
        # 替换巢穴信息
        spread_str = re.sub(r"\{{2}巢穴\|([ap])\|([0-9|]*)}{2}", cave_replace, spread_str)
        # 替换 tt
        spread_str = re.sub(r"{{tt\|\*\|([^{}]*)}}", "(\\1)", spread_str)
        # spread_str_grouped = re.findall(r"{{分布/main\|([0-9]*)\|([A-Z]*\|){5}([^|]*)\|([^|]*)\|([^|]*)\|[^|}]*}}", spread_str)
        spread_split = spread_str.split("|")
        print(spread_str.split("|"))
        spread_location = spread_split[7].replace("\n", "")
        spread_path = spread_split[8].replace("\n", "")
        spread_note = ""
        if len(spread_split) >= 10:
            spread_note = spread_split[9].replace("}}", "").replace("\n", "")
        else:
            spread_path = spread_path.replace("}}", "")
        print("Location", spread_location,
              "Path", spread_path,
              "Note", spread_note)

    # 匹配种族值
    print("===种族值===")
    species_strength_str = re.findall(r"{{种族值(|\S*?\n)}{2}?")


if __name__ == '__main__':
    test_pokemon_names = ("波克基斯", "阿尔宙斯")
    for test_pokemon_name in test_pokemon_names:
        get_pokemon_info(test_pokemon_name)
    while True:
        pokemon_name = input("输入宝可梦名称:")
        get_pokemon_info("波克基斯")

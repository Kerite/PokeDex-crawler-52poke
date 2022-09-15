import csv
import requests
from bs4 import BeautifulSoup
import re

proxies = {
    'http': '127.0.0.1:7890',
    'https': '127.0.0.1:7890'
}

pokemon_types = {
    "一般": "NORMAL",
    "草": "GRASS",
    "火": "FIRE",
    "水": "WATER",
    "电": "ELECTRIC",
    "飞行": "FLYING",
    "超能力": "PSYCHIC",
    "虫": "BUG",
    "岩石": "ROCK",
    "幽灵": "GHOST",
    "冰": "ICE",
    "龙": "DRAGON",
    "格斗": "FIGHT",
    "恶": "DARK",
    "毒": "POISON",
    "钢": "STEEL",
    "地面": "GROUND",
    "妖精": "FAIRY",
    "": ""
}


def update_pokemon_list():
    style_url = "https://wiki.52poke.com/load.php?lang=zh-hans&modules=ext.gadget.msp"
    r = requests.get(style_url, proxies=proxies)
    styles = re.findall(r"\.(sprite-icon-[0-9a-zA-Z]*?)\{background-position:([\-0-9]*?)(px)? ([\-0-9]*?)(px)?}",
                        r.text)
    style_dict = {}
    for style in styles:
        style_dict[style[0]] = (abs(int(int(style[1]) / 68)), abs(int(int(style[3]) / 56)))

    print(style_dict)
    url = "https://wiki.52poke.com/zh-hans/pmlist"
    r = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(r.text, features="html.parser")

    tables = soup.find_all("table", "eplist")
    with open('pokemon_list.csv', 'w', newline='', encoding='UTF-8') as csv_file:
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
                    pokemon_num = tds[0].string.replace('#', '').replace("\n", '')
                    pokemon_name = tds[2].a.string
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
                        int(pokemon_num), pokemon_name, pokemon_sub_name, pokemon_types[pokemon_type1],
                        pokemon_types[pokemon_type2], generation, pokemon_icon_location_y, pokemon_icon_location_x,
                        pokemon_icon_location
                    ])
                    pokemon_writer.writerow([
                        int(pokemon_num), pokemon_name, pokemon_sub_name, pokemon_types[pokemon_type1],
                        pokemon_types[pokemon_type2], generation, pokemon_icon_location_y, pokemon_icon_location_x
                    ])
            generation = generation + 1


if __name__ == '__main__':
    update_pokemon_list()

import csv
import os.path
import pathlib
import sqlite3
from abc import abstractmethod
from enum import Enum
from io import BytesIO

import requests
from PIL import Image
from bs4 import BeautifulSoup
from typing.io import TextIO

from src.value_map_dict import special_pokemon_form_name_map

proxies = {
    'http': '127.0.0.1:7890',
    'https': '127.0.0.1:7890'
}


def request_get(url: str):
    while True:
        try:
            return requests.get(url, proxies=proxies)
        except requests.exceptions.ProxyError:
            print("Error, Retrying")
            continue
        except requests.exceptions.SSLError:
            continue


def request_parse(url: str):
    req = request_get(url)
    print("ParsingUrl", url)
    return BeautifulSoup(req.text, features="html.parser")


def get_specie_strength(
        species_strength_dic: dict,
        pokemon_dex_name: str,
        form_name: str
):
    # 宝可梦只有一种形态
    if form_name is None:
        # 宝可梦的图鉴名字就在字典里
        if pokemon_dex_name in species_strength_dic:
            result = species_strength_dic[pokemon_dex_name]
        # 宝可梦的图鉴名字不在字典里则在字典里寻找以下键
        else:
            for judge_key in ['第六世代起', '第七世代起', '第七世代起', '一般', '一般的样子']:
                if judge_key in species_strength_dic:
                    result = species_strength_dic[judge_key]
    else:
        print('Form', pokemon_dex_name, form_name, species_strength_dic)
        if (pokemon_dex_name in special_pokemon_form_name_map) and (
                form_name in special_pokemon_form_name_map[pokemon_dex_name]):
            print(special_pokemon_form_name_map[pokemon_dex_name][form_name])
            result = species_strength_dic[special_pokemon_form_name_map[pokemon_dex_name][form_name]]
        elif form_name == pokemon_dex_name:
            result = fall_back_find(pokemon_dex_name, species_strength_dic, form_name)
        elif ('伽勒爾' in form_name) or ('伽勒尔' in form_name):
            result = species_strength_dic['伽勒尔的样子']
        elif '洗翠' in form_name:
            result = species_strength_dic['洗翠的样子']
        elif '阿罗拉' in form_name:
            if '阿罗拉的样子' in species_strength_dic:
                result = species_strength_dic['阿罗拉的样子']
            else:
                result = fall_back_find(pokemon_dex_name, species_strength_dic, form_name)
        elif '超极巨化' in form_name:
            if '一般' in species_strength_dic:
                result = species_strength_dic['一般']
            else:
                result = species_strength_dic['一般的样子']
        elif '超级' in form_name:
            result = species_strength_dic['超级进化']
        else:
            result = fall_back_find(pokemon_dex_name, species_strength_dic, form_name)
    print("种族值", result, form_name)
    return result


def fall_back_find(
        pokemon_dex_name: str,
        species_strength_dic: dict,
        form_name: str
):
    if pokemon_dex_name in species_strength_dic:
        return species_strength_dic[pokemon_dex_name]
    elif '第六世代起' in species_strength_dic:
        return species_strength_dic['第六世代起']
    elif '第七世代起' in species_strength_dic:
        return species_strength_dic['第七世代起']
    elif '一般' in species_strength_dic:
        return species_strength_dic['一般']
    elif '一般的样子' in species_strength_dic:
        return species_strength_dic['一般的样子']
    else:
        return species_strength_dic[form_name]


def flat_list(input_list: list):
    final_list = []
    for item in input_list:
        # print(type(item))
        if isinstance(item, list):
            for inner_item in item:
                final_list.append(inner_item)
        else:
            final_list.append(item)
    # print(final_list)
    return final_list


def download_media(media_name: str, saved_name: str):
    if os.path.exists("./pokemon_images/" + saved_name.replace('<br>', '') + '.webp'):
        return
    print("MediaLink", "https://wiki.52poke.com/wiki/File:" + media_name)
    req = request_get("https://wiki.52poke.com/wiki/File:" + media_name.replace('|', '').replace('_.png', '.png'))
    h = BeautifulSoup(req.text, features="html.parser")
    div = h.find("div", "fullImageLink")
    print("Found Div", div)
    print("Found Element", div.find("img").attrs['src'])
    image = Image.open(BytesIO(request_get("https:" + div.find("img").attrs['src']).content))
    image.save("./pokemon_images/" + saved_name.replace('<br>', '') + '.webp', format='webp')
    return


default_sqlite_path = pathlib.Path(
    r"D:\Projects\AndroidProjects\PokeDex\app\src\main\assets\database\pokedex.db")


class OutputType(Enum):
    CSV = 0
    SQLITE = 1
    NO_OUT_PUT = 2


class SpiderBase:
    __output_type: OutputType
    __output_path: pathlib.Path
    _connection: sqlite3.Connection
    _cursor: sqlite3.Cursor
    __csv_file: TextIO
    __csv_writer: csv.writer

    def __init__(self, output_type=OutputType.SQLITE, output_path: pathlib.Path = pathlib.Path("./pokemon.db")):
        """
        ;
        :param output_type: 输出的类型 SQLITE 或者为 CSV
        """
        self.__output_type = output_type
        self.__output_path = output_path
        if output_type == OutputType.SQLITE:
            print("Sqlite Mode")
            self._connection = sqlite3.connect(output_path)
            self._cursor = self._connection.cursor()
            self._init_database()
        elif output_type == OutputType.CSV:
            print("Csv Mode")
            self.__csv_file = open(output_path, 'w', newline='', encoding='UTF-8')
            self.__csv_writer = csv.writer(self.__csv_file, quoting=csv.QUOTE_NONNUMERIC)

    def _save_data(self, data: list):
        if self.__output_type == OutputType.SQLITE:
            self._save_sqlite(data)
        elif self.__output_type == OutputType.CSV:
            self._save_sqlite(data)
        elif self.__output_type == OutputType.NO_OUT_PUT:
            return

    def _save_csv(self, data: list):
        self.__csv_writer.writerow(data)

    def __del__(self):
        if self.__output_type == OutputType.SQLITE:
            self._connection.close()
        elif self.__output_type == OutputType.CSV:
            self.__csv_file.close()

    @abstractmethod
    def _save_sqlite(self, data: list):
        pass

    @abstractmethod
    def _init_database(self):
        pass

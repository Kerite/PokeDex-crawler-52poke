"""
保存特性列表到数据库
"""
import csv
import sqlite3
from pathlib import Path

from bs4 import BeautifulSoup, PageElement
from typing.io import TextIO

from src import utils
from src.utils import OutputType
from opencc import OpenCC


class PokemonAbilitySpider:
    """
    爬取宝可梦的特性列表
    """
    __output_type: OutputType
    __output_path: Path
    _connection: sqlite3.Connection
    __cursor: sqlite3.Cursor
    __csv_file: TextIO
    __csv_writer: csv.writer

    def __init__(self, output_type=OutputType.SQLITE, output_path: Path = Path("./pokemon.db")):
        """
        ;
        :param output_type: 输出的类型 SQLITE 或者为 CSV
        """
        self.__output_type = output_type
        self.__output_path = output_path
        if output_type == OutputType.SQLITE:
            print("Sqlite Mode")
            self._connection = sqlite3.connect(output_path)
            self.__cursor = self._connection.cursor()
            self._init_database()
        elif output_type == OutputType.CSV:
            print("Csv Mode")
            self.__csv_file = open(output_path, 'w', newline='', encoding='UTF-8')
            self.__csv_writer = csv.writer(self.__csv_file, quoting=csv.QUOTE_NONNUMERIC)

    def _init_database(self):
        self.__cursor.execute('DROP TABLE IF EXISTS pokemon_ability')
        self.__cursor.execute('CREATE TABLE pokemon_ability('
                              '  id INTEGER PRIMARY KEY AUTOINCREMENT,'
                              '  name TEXT NOT NULL,'
                              '  jp_name TEXT NOT NULL,'
                              '  en_name TEXT NOT NULL,'
                              '  description TEXT NOT NULL,'
                              '  generation INTEGER NOT NULL'
                              ')')
        self._connection.commit()

    def fetch_pokemon_ability_list(self):
        """
        获取宝可梦特性列表
        """
        ability_list_url = "https://wiki.52poke.com/wiki/%E7%89%B9%E6%80%A7%E5%88%97%E8%A1%A8"
        req = utils.request_get(ability_list_url)
        converter = OpenCC()
        source_str = converter.convert(req.text)
        bs = BeautifulSoup(source_str, features="html.parser")
        source = bs.find_all('table', 'eplist')
        print(len(source))

        for (idx, table) in enumerate(source):
            print(table.attrs['class'])
            for row in table.find_all('tr'):
                tds: list[PageElement] = row.find_all('td')
                if len(tds) != 7:
                    continue
                [ability_id, name_element, jp_name, en_name, description, _, _] = tds
                name: str = name_element.a.string
                values = [ability_id.string.strip(), name, jp_name.string.strip(), en_name.string.strip(),
                          description.string.strip(), 3 + idx]
                print(values)
                self._save_data(values)
        del self

    def _save_data(self, data: list):
        if self.__output_type == OutputType.SQLITE:
            self._save_sqlite(data)
        elif self.__output_type == OutputType.CSV:
            self._save_sqlite(data)

    def _save_sqlite(self, data: list):
        self.__cursor.execute('INSERT INTO pokemon_ability(id, name, jp_name, en_name, description, generation) '
                              'VALUES (?, ?, ?, ?, ?, ?)', data)
        self._connection.commit()

    def _save_csv(self, data: list):
        self.__csv_writer.writerow(data)

    def __del__(self):
        if self.__output_type == OutputType.SQLITE:
            self._connection.close()
        elif self.__output_type == OutputType.CSV:
            self.__csv_file.close()

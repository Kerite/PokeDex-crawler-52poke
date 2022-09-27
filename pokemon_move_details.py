"""
技能详细信息
"""
import json
import re
from abc import ABC
from pathlib import Path

import opencc

import constants
import utils
import value_map_dict
from constants import generation_count
from pokemon_move import PokemonMoveSpider
from utils import SpiderBase, OutputType
from value_map_dict import game_code_to_generation_dict, learn_set_table_column_mapping


def _test_function(move_item: list[str], move_add_generation: int):
    addition_notes: dict[str, str] = {}  # 额外的无用信息（可能）
    special_form: str | None = None
    if move_item[3].startswith('form'):
        special_form = move_item[3].strip('form=')
        move_item.remove(move_item[3])
    learn_list = [{} for _ in range(generation_count)]
    # 宝可梦图鉴编号
    move_item_pokemon_dex_number = move_item[1]
    # 宝可梦名字
    move_item_pokemon_name = move_item[2]
    # 宝可梦属性1（可以跳过）
    move_item_pokemon_type1 = move_item[3]
    # 宝可梦属性2（可以跳过）
    move_item_pokemon_type2 = move_item[4]
    current_generation = move_add_generation
    # print("Move Item", move_item)
    for move_item_column in move_item[5:]:
        if current_generation > generation_count:
            continue
        if move_item_column.__contains__('='):
            print("(特殊版本)")
            [equal_left, equal_right] = move_item_column.split('=')
            if equal_left in ['except', 'v', 'alt', 'note', 'no']:
                addition_notes[equal_left] = equal_right
            elif equal_left == 'form':
                special_form = equal_right
            else:
                learn_list[current_generation - 2][equal_left] = equal_right
        else:
            print("正常世代", current_generation)
            if move_item_column != '':
                learn_list[current_generation - 1]['default'] = move_item_column
            current_generation += 1
    if special_form is not None:
        print(move_item[2] + "(" + special_form + ")", learn_list)
    else:
        print(move_item[2], learn_list)
    for (idx, item) in enumerate(learn_list):
        print('  - 第' + (idx + 1).__str__() + '世代', item)
    return special_form, learn_list


class ArgumentError(Exception):
    pass


class LearnSetTutorialAll:
    """
    用于解析 传授技能的行
    """
    __row: list[str]
    pokemon_form: str | None = None
    per_generation_data = [False] * constants.tutorial_all_game_list.__len__()
    additional_info = {}
    dex_number = 0

    def __init__(self, row: list[str]):
        self.__row = row
        temp = row[5]
        if len(row) < 4:
            raise ArgumentError
        if temp.startswith('form='):
            self.pokemon_form = temp.strip('form=')
            row.remove(temp)
        self.dex_number = int(row[1])
        pokemon_name: str = row[2]
        type_1: str = row[3]
        type_2: str | None = row[4]
        for (sub_index, column_str) in enumerate(row[5:]):
            if column_str.__contains__('='):
                [column_equal_left, column_equal_right] = column_str.split('=')
                if column_equal_left in ['alt', 'note', 'v']:
                    self.additional_info[column_equal_left] = column_equal_right
            if column_str.strip() == '':
                self.per_generation_data[sub_index + 1] = False
            else:
                self.per_generation_data[sub_index + 1] = True

    def pack(self):
        return {
            'dex_number': self.dex_number,
            'source': 'TUTORIAL',
            'data': self.per_generation_data,
            'form': self.pokemon_form
        }


class PokemonMoveDetailsSpider(SpiderBase, ABC):
    """
    爬取宝可梦技能详情
    """

    def __init__(self, output_type=OutputType.SQLITE, output_path: Path = Path("./pokemon.db")):
        super(PokemonMoveDetailsSpider, self).__init__(output_type, output_path)

    def _init_database(self):
        self._cursor.execute(
            'DROP TABLE IF EXISTS pokemon_move_basic'
        )
        self._cursor.execute(
            'CREATE TABLE pokemon_move_basic('
            '   id INTEGER PRIMARY KEY AUTOINCREMENT,'
            '   move_id INTEGER,'
            '   name TEXT NOT NULL,'
            '   jp_name TEXT NOT NULL,'
            '   en_name TEXT NOT NULL,'
            '   type TEXT NOT NULL,'
            '   damage_category TEXT NOT NULL,'
            '   pp INTEGER NOT NULL,'
            '   power TEXT NOT NULL,'
            '   accuracy TEXT NOT NULL,'
            '   generation INTEGER NOT NULL,'
            '   touches INTEGER NOT NULL, --是否为接触招式--\n'
            '   protect INTEGER NOT NULL, --是否可以被守住--\n'
            '   magic_coat INTEGER NOT NULL, --是否受魔法反射影响\n'
            '   snatch INTEGER NOT NULL, -- 是否可以被抢夺\n'
            '   mirror_move INTEGER NOT NULL, -- 是否可以被鹦鹉学舌影响\n'
            '   kings_rock INTEGER NOT NULL, -- 是否受王者之证等道具影响\n'
            '   sound INTEGER NOT NULL, --是否是声音招式\n'
            '   target INTEGER NOT NULL --技能影响范围\n'
            ')'
        )
        self._connection.commit()
        self._cursor.execute(
            'CREATE INDEX index_move_id ON pokemon_move_basic(move_id)'
        )
        self._connection.commit()
        self._cursor.execute(
            'DROP TABLE IF EXISTS pokemon_move_learn'
        )
        self._cursor.execute(
            'CREATE TABLE pokemon_move_learn('
            '   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
            '   move_table_id INTEGER NOT NULL,'
            '   pokemon_details_id INTEGER NOT NULL,'
            '   learn_source VARCHAR(10) NOT NULL,'
            '   gen1 TEXT,'
            '   gen2 TEXT,'
            '   gen3 TEXT,'
            '   gen4 TEXT,'
            '   gen5 TEXT,'
            '   gen6 TEXT,'
            '   gen7 TEXT,'
            '   gen8 TEXT'
            ')'
        )
        self._connection.commit()

    def fetch(self, move_list: list):
        """
        拉取宝可梦技能信息列表
        :param move_list:
        :return:
        """
        for (idx, [move_num, name, _, _, _, _, _, _, _, _, _]) in enumerate(move_list):
            self.process_single_move(name)

    def process_single_move(self, move_name: str):
        learn_list = []
        req = utils.request_parse(r"https://wiki.52poke.com/index.php?title=" + move_name + r"（招式）&action=edit")
        # print("Request", req)
        source_code = req.find("textarea").string
        converter = opencc.OpenCC()
        source_code = converter.convert(source_code)

        '''
        处理基础信息（页面右上角的面板)
        '''
        print("======================================")
        print("=           开始解析基本信息           =")
        print("======================================\n")
        basic_info_dict = {}
        basic_info = re.findall(r"{{招式信息框([\s\S]*?)==", source_code)[0].replace('\n', '')[:-2]
        clear_basic_info = re.sub(r"{{([\s\S]*?)}}", "", basic_info)
        print("整理后的基本信息源码(clear_basic_info):", clear_basic_info)
        basic_info_list = re.findall(r"\|(.*?)=([^|]*)", clear_basic_info)
        # print("BasicInfoList", basic_info_list)
        for (basic_info_key, basic_info_value) in basic_info_list:
            basic_info_dict[basic_info_key] = basic_info_value.strip()
        print("获取的基本信息(basic_info_dict):", basic_info_dict)
        print("\n============技能基本信息解析完毕============\n")

        '''
        处理可以学会该招式的宝可梦
        当startGen为2以后时，去皮去伊视作不存在，除非指定
        '''
        print("======================================")
        print("=           开始解析学习列表           =")
        print("======================================\n")
        move_list_level_str = re.sub(r"{{(?!Movelist)(?P<content>.[^{^}]*?)}}", _process_special, source_code)
        # 这行获取招式学习器表格的表头(eg.'一般|2||TM17|TM17|TM17|TM17|TM17|TM17|LPLE=TM07|TM25')
        tm_move_header_src_list = re.findall(r"{{Movelistheader\|学习器\|([\s\S]*?)}}", source_code)
        # 因为有的技能没有技能机的获取方式所以加个判断
        tm_list = [{} for _ in range(generation_count)]
        if len(tm_move_header_src_list) > 0:
            tm_move_header_src = tm_move_header_src_list[0]
            split_tm_move_header = tm_move_header_src.split('|')
            print("技能机表格头源码", tm_move_header_src)
            tm_start_generation = int(split_tm_move_header[1])
            current_append_index = tm_start_generation - 1
            # 遍历技能机表头的从第3格 + 技能机加入的世代到最后
            for tm_str in split_tm_move_header[(1 + tm_start_generation):]:
                # print(idx + tm_start_generation - 1)
                if tm_str.__contains__('='):
                    [tm_item_key, tm_item_value] = tm_str.split('=')
                    tm_list[value_map_dict.game_code_to_generation_dict[tm_item_key] - 1][tm_item_key] = tm_item_value
                else:
                    tm_list[current_append_index]['default'] = tm_str
                    current_append_index += 1
            print("技能机列表", tm_list)
        # 每个表格行的源码由{{Movelist/获取方式/技能加入的世代(all,gen1,gen2,gen3...)|.....}}
        move_list: list[str] = re.findall(r"{{Movelist/[\s\S]*?}}", move_list_level_str)
        for move_item in move_list:
            print(move_item)
            move_item = move_item.strip('{').strip('}').split('|')
            move_item_prefix_list = move_item[0].split('/')
            move_learn_type = move_item_prefix_list[1]
            if move_item_prefix_list[2] == 'all':
                move_add_generation = 1
            else:
                move_add_generation = int(move_item_prefix_list[2].strip('gen'))
            print("技能获取的方式(move_learn_type):", move_learn_type)
            print("加入的世代:", move_add_generation)
            match move_learn_type:
                case 'level':  # 升级技能条目
                    (special_form, learn_column) = _test_function(move_item, move_add_generation)
                    learn_list.append({
                        'dex_number': int(move_item[1]),
                        'source': 'LEVEL',
                        'data': learn_column,
                        'form': special_form
                    })
                case 'tm':  # 技能机条目
                    print("各世代的技能机:", tm_list)
                    (special_form, learn_column) = _test_function(move_item, move_add_generation)
                    learn_list.append({
                        'dex_number': int(move_item[1]),
                        'source': 'TM_MACHINE',
                        'data': learn_column,
                        'form': special_form
                    })
                case 'breed':  # 通过遗传
                    (special_form, learn_column) = _test_function(move_item, move_add_generation)
                    learn_list.append({
                        'dex_number': int(move_item[1]),
                        'source': 'BREED',
                        'data': learn_column,
                        'form': special_form
                    })
            print("===一行结束===\n")
        print("\n============宝可梦学习列表（不包括教授招式）解析完毕============\n")

        print("======================================")
        print("=           开始解析教授列表           =")
        print("======================================")
        print()
        learn_set_str_list: list[str] = re.findall(r"{{learnset/[\s\S]*?}}", source_code)
        for learn_set_item_str in learn_set_str_list:
            learn_item_group = learn_set_item_str.strip('{').strip('}').split('|')
            learn_set_type = learn_item_group[0].split('/')[1]
            print("LearnSet类型", learn_set_item_str)
            match learn_set_type:
                case 'tutorall':
                    packed_data = LearnSetTutorialAll(learn_item_group).pack()
                    learn_list.append(packed_data)
                    print("解析到的数据：", packed_data)
            print("===一行结束===")
            print()

        print("============End============\n")
        for learn_row in learn_list:
            if learn_row == {}:
                continue
            cur = self._connection.cursor()
            cur.execute(
                'SELECT id FROM pokemon_move WHERE name = ?',
                [move_name]
            )
            move_id = cur.fetchall()[0][0]
            cur.close()
            cur = self._connection.cursor()
            print(learn_row)
            pokemon_id = None
            if learn_row['form'] is not None:
                fetched_pokemons = cur.execute(
                    'SELECT id FROM pokemon_detail WHERE dex_number = ? AND form_name LIKE \'%\' || ? || \'%\'',
                    [learn_row['dex_number'], learn_row['form']]
                ).fetchall()
                print("Selected Pokemon", [learn_row['dex_number'], learn_row['form']], fetched_pokemons)
                pokemon_id = fetched_pokemons[0][0]
            else:
                pokemon_id = cur.execute(
                    'SELECT id FROM pokemon_detail WHERE dex_number = ?',
                    [learn_row['dex_number']]
                ).fetchall()[0][0]
                print("Selected Pokemon", pokemon_id)

            input_data = [move_id, pokemon_id, learn_row['source']]
            for learn_row_data in learn_row['data']:
                input_data.append(json.dumps(learn_row_data))
            print("Input data", input_data)

            self._connection.execute(
                'INSERT INTO pokemon_move_learn('
                'move_table_id, pokemon_details_id, learn_source,'
                'gen1, gen2, gen3, gen4, gen5, gen6, gen7, gen8)'
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                input_data
            )
            self._connection.commit()
        return learn_list


def _process_special(match: re.Match):
    """
    处理网页中显示为宝可梦缩略图的内容
    """
    matched_str = match.group('content')
    split_matched = matched_str.split('|')
    match split_matched[0]:
        case 'MSP':
            return 'PM(' + split_matched[1] + '-' + split_matched[2] + '),'
    return matched_str


if __name__ == '__main__':
    # result_list = PokemonMoveDetailsSpider(output_path=utils.default_sqlite_path).process_single_move('地球上投')
    # print(json.dumps(result_list))
    moves = PokemonMoveSpider(OutputType.NO_OUT_PUT).fetch()
    PokemonMoveDetailsSpider(output_path=utils.default_sqlite_path).fetch(moves)

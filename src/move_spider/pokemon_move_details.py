"""
技能详细信息
"""
import re
from abc import ABC
from pathlib import Path
from urllib.parse import unquote

import opencc

import __utils as privateUtils
from src import utils, value_map_dict
from src.constants import generation_count
from src.move_spider.move_row_parsers import MoveListRowParser
from src.move_spider.pokemon_move import PokemonMoveSpider
from src.utils import SpiderBase, OutputType


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
            [equal_left, equal_right] = move_item_column.split('=')
            if equal_left in ['except', 'v', 'alt', 'note', 'no']:
                addition_notes[equal_left] = equal_right
            elif equal_left == 'form':
                special_form = equal_right
            else:
                learn_list[current_generation - 2][equal_left] = equal_right
        else:
            # print('[DEBUG]', "第", current_generation, '世代读取到数据')
            if move_item_column != '':
                learn_list[current_generation - 1]['default'] = move_item_column
            current_generation += 1
    if special_form is not None:
        print(move_item[2] + "(" + special_form + ")", learn_list)
    else:
        print('  - 宝可梦', move_item[2], learn_list)
    for (idx, item) in enumerate(learn_list):
        print('    - 第' + (idx + 1).__str__() + '世代', item)
    return special_form, learn_list


class PokemonMoveDetailsSpider(SpiderBase, ABC):
    """
    爬取宝可梦技能详情
    """

    def __init__(self, output_type=OutputType.SQLITE, output_path: Path = Path("./pokemon.db")):
        super(PokemonMoveDetailsSpider, self).__init__(output_type, output_path)

    def _init_database(self):
        # <editor-fold defaultstate="collapsed" desc="初始化数据库">
        privateUtils.create_move_basic_table(self._connection)
        privateUtils.create_move_teach_table(self._connection)
        privateUtils.create_move_learn_table(self._connection)
        # </editor-fold>

    def fetch(self, move_list: list):
        """
        拉取宝可梦技能信息列表
        :param move_list:
        :return:
        """
        for (idx, [move_num, name, _, _, _, _, _, _, _, _, _, url]) in enumerate(move_list):
            name = unquote(url.split('/')[-1])
            self.process_single_move(name)

    def process_single_move(self, move_name: str):
        from src.constants import PRINT_PREFIX_DEBUG, PRINT_SUFFIX, PRINT_PREFIX_HEADLINE
        for _ in range(2):
            print()
        print('解析技能', move_name)
        from move_row_parsers import LearnSetTutorialAllParser
        learn_list = []
        req = utils.request_parse(r"https://wiki.52poke.com/index.php?title=" + move_name + r"&action=edit")
        move_name = move_name.split('（')[0]
        source_code = req.find("textarea").string
        converter = opencc.OpenCC()
        source_code = converter.convert(source_code)
        move_name = converter.convert(move_name)
        '''
        处理基础信息（页面右上角的面板)
        '''
        print(PRINT_PREFIX_HEADLINE)
        print("======================================")
        print("=           开始解析基本信息            =")
        print("======================================" + PRINT_SUFFIX)
        basic_info_dict = {
            'n': None,
            'name': None,
            'jname': None,
            'enname': None,
            'type': None,
            'damagecategory': None
        }
        # <editor-fold defaultstate="collapsed" desc="解析基本信息">
        basic_info = re.findall(r"{{招式信息框([\s\S]*?)==", source_code)[0].replace('\n', '')[:-2]
        clear_basic_info = re.sub(r"{{([\s\S]*?)}}", "", basic_info)
        print("整理后的基本信息源码(clear_basic_info):", clear_basic_info)
        basic_info_list = re.findall(r"\|(.*?)=([^|]*)", clear_basic_info)
        for (basic_info_key, basic_info_value) in basic_info_list:
            basic_info_dict[basic_info_key] = basic_info_value.strip()
        # </editor-fold>
        print("获取的基本信息(basic_info_dict):", basic_info_dict)
        for temp_basic_info_key in ['touches', 'protect', 'magiccoat', 'snatch',
                                    'mirrormove', 'kingsrock', 'sound']:
            if temp_basic_info_key not in basic_info_dict.keys():
                basic_info_dict[temp_basic_info_key] = None
        if 'target' not in basic_info_dict:
            basic_info_dict['target'] = 0
        insert_basic_array = [
            basic_info_dict['n'], basic_info_dict['name'],
            basic_info_dict['jname'], basic_info_dict['enname'],
            value_map_dict.pokemon_types[basic_info_dict['type']],
            value_map_dict.DAMAGE_CATEGORY_MAP_DICT[basic_info_dict['damagecategory']],
            basic_info_dict['basepp'], basic_info_dict['power'], basic_info_dict['accuracy'],
            basic_info_dict['gen'],
            value_map_dict.BOOL_MAPPING_DICT[basic_info_dict['touches']],
            value_map_dict.BOOL_MAPPING_DICT[basic_info_dict['protect']],
            value_map_dict.BOOL_MAPPING_DICT[basic_info_dict['magiccoat']],
            value_map_dict.BOOL_MAPPING_DICT[basic_info_dict['snatch']],
            value_map_dict.BOOL_MAPPING_DICT[basic_info_dict['mirrormove']],
            value_map_dict.BOOL_MAPPING_DICT[basic_info_dict['kingsrock']],
            value_map_dict.BOOL_MAPPING_DICT[basic_info_dict['sound']],
            basic_info_dict['target']
        ]
        privateUtils.insert_basic_info(self._connection, insert_basic_array)
        print(f"{PRINT_PREFIX_HEADLINE}============技能基本信息解析完毕============{PRINT_SUFFIX}")

        print(PRINT_PREFIX_HEADLINE)
        print("======================================")
        print("=           开始解析学习列表            =")
        print("======================================" + PRINT_SUFFIX)
        move_list_level_str = re.sub(r"{{(?!Movelist)(?P<content>.[^{^}]*?)}}", _process_special, source_code)
        move_list: list[str] = re.findall(r"{Movelist/[\s\S]*?}", move_list_level_str)
        for move_item in move_list:
            print(f'{PRINT_PREFIX_DEBUG}源码:', f'{move_item}{PRINT_SUFFIX}')
            print('  - 技能名', move_name)
            move_item = move_item.strip('{').strip('}').replace('\n', '').split('|')
            _parser = MoveListRowParser(move_item)
            _parser.print_debug_info()
            move_id = privateUtils.select_move_id(
                connection=self._connection,
                move_name=move_name,
            )
            _parser.insert_data(
                connection=self._connection,
                move_id=move_id
            )
        print(f"{PRINT_PREFIX_HEADLINE}============ 宝可梦学习列表（不包括教授招式）解析完毕 ============{PRINT_SUFFIX}")

        print(PRINT_PREFIX_HEADLINE)
        print("======================================")
        print("=           开始解析教授列表            =")
        print(f"======================================{PRINT_SUFFIX}")
        learn_set_str_list: list[str] = re.findall(r"{learnset/[\s\S]*?}", source_code)
        for learn_set_item_str in learn_set_str_list:
            print(f'{PRINT_PREFIX_DEBUG}{learn_set_item_str}{PRINT_SUFFIX}')
            learn_item_group = learn_set_item_str.strip('{').strip('}').replace('\n', '').split('|')
            learn_set_type = learn_item_group[0].split('/')[1]
            print("  - LearnSet", '技能教授')
            print("    - 类型", learn_set_type)
            match learn_set_type:
                case 'tutorall':
                    print("    - 技能名", move_name)
                    # <editor-fold defaultstate="collapsed" desc="解析数据并插入数据库">
                    selected_move_id = privateUtils.select_move_id(move_name, self._connection)
                    _parser = LearnSetTutorialAllParser(row=learn_item_group, move_id=selected_move_id)
                    packed_data = _parser.pack_debug_print_data()
                    _parser.insert_database(connection=self._connection)
                    learn_list.append(packed_data)
                    # </editor-fold>
                case _:
                    print(f'{PRINT_PREFIX_DEBUG}[DEBUG]', '跳过解析')
            print()

        print(f"{PRINT_PREFIX_HEADLINE}============ 宝可梦教授列表解析完毕 ============{PRINT_SUFFIX}")
        return learn_list


def _process_special(match: re.Match):
    """
    处理网页中显示为宝可梦缩略图的内容
    """
    try:
        matched_str = match.group('content')
        split_matched = matched_str.split('|')
        match split_matched[0]:
            case 'MSP':
                if len(split_matched) > 2:
                    return 'PM(' + split_matched[1] + '-' + split_matched[2] + '),'
                else:
                    return f'PM({split_matched[1]}),'
            case 'MSPN':
                return f'PMS({split_matched[1]})'
        return matched_str
    except IndexError:
        print('\033[1;33m', '字符串匹配数组越界', match.group('content'), '\033[0m')
        raise


if __name__ == '__main__':
    # result_list = PokemonMoveDetailsSpider(output_path=utils.default_sqlite_path).process_single_move('突袭（招式）')
    # print(json.dumps(result_list))
    # 获取技能列表
    moves = PokemonMoveSpider(OutputType.NO_OUT_PUT).fetch()
    PokemonMoveDetailsSpider(output_path=utils.default_sqlite_path).fetch(moves)

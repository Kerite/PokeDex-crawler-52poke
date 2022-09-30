import sqlite3
from sqlite3 import Connection

from src.constants import *


class ArgumentError(Exception):
    pass


class HeaderTmParser:
    tm_list: list[dict]

    def __init__(self, header_str: str):
        # <editor-fold defaultstate="collapsed" desc="解析技能机表头源码">
        from src import value_map_dict

        self.tm_list = [{} for _ in range(generation_count)]
        split_tm_move_header = header_str.replace('\n', '').split('|')
        tm_start_generation = int(split_tm_move_header[1])
        current_append_index = tm_start_generation - 1
        for tm_str in split_tm_move_header[(1 + tm_start_generation):]:
            # print(idx + tm_start_generation - 1)
            if tm_str.__contains__('='):
                [tm_item_key, tm_item_value] = tm_str.split('=')
                self.tm_list[value_map_dict.game_code_to_generation_dict[tm_item_key] - 1][tm_item_key] = tm_item_value
            else:
                try:
                    self.tm_list[current_append_index]['default'] = tm_str
                except IndexError:
                    print('分隔后的数组', split_tm_move_header)
                    print('技能机数组越界', 'Current Index', current_append_index, 'TM list', self.tm_list)
                current_append_index += 1
        # </editor-fold>


class LearnSetTutorialAllParser:
    """
    用于解析 传授技能的行
    """
    pokemon_form: str | None = None
    per_generation_data: list
    additional_info: dict
    dex_number = 0
    pokemon_name: str
    __move_id: int
    __pokemon_id: int
    __row: list[str]

    def __inner_determine_delete_column(self, column: str):
        # <editor-fold defaultstate="collapsed" desc="处理">
        if column.__contains__('='):
            [column_equal_left, column_equal_right] = column.split('=')
            if column_equal_left in ['alt', 'note', 'gender', 'except', 'lt', 'gen', 'v']:
                self.additional_info[column_equal_left] = column_equal_right
            elif column_equal_left == 'form':
                self.pokemon_form = column_equal_right
            elif column_equal_left.isdigit():
                if column_equal_right in ['yes', '1']:
                    column_game_index = int(column_equal_left) - 1
                    game_key = GAME_FULL_LIST[column_game_index]
                    self.per_generation_data[tutorial_all_game_list.index(game_key)] = True
            else:
                if column_equal_right in ['yes', '1']:
                    self.per_generation_data[tutorial_all_game_list.index(column_equal_left)] = True
            return True
        else:
            return False
        # </editor-fold>

    def __init__(self, row: list[str], move_id: int):
        # <editor-fold desc="初始化并解析" defaultstate="collapsed">
        self.__row = row
        self.__move_id = move_id
        self.per_generation_data = [False for _ in range(tutorial_all_game_list.__len__())]
        self.additional_info = {
            'gen': None,
            'except': None,
            'note': None,
            'gender': None,
            'form': None
        }
        print(f'{PRINT_PREFIX_DEBUG}    - [DEBUG]', '整理前的Row', f'{row}{PRINT_SUFFIX}')
        row = [column_str for column_str in row if not self.__inner_determine_delete_column(column_str)]
        print(f'{PRINT_PREFIX_DEBUG}    - [DEBUG]', '整理后的Row', f'{row}{PRINT_SUFFIX}')
        if len(row) < 4:
            raise ArgumentError
        self.dex_number = int(row[1])
        self.pokemon_name: str = row[2]
        type_1: str = row[3]
        if row.__len__() > 4:
            type_2: str | None = row[4]
        for (sub_index, column_str) in enumerate(row[5:]):
            if column_str.strip() == '':
                self.per_generation_data[sub_index] = False
            elif column_str.strip() == 'no':
                self.per_generation_data[sub_index] = False
            else:
                print(f"{PRINT_PREFIX_DEBUG}      - [DEBUG]", '找到下标为', sub_index + 5, '内容为',
                      f'{column_str}', '表示在', TUTORIAL_ALL_GAME_LIST_CN[sub_index],
                      f'可以学习{PRINT_SUFFIX}')
                self.per_generation_data[sub_index] = True
        # </editor-fold>

    def pack(self):
        # <editor-fold defaultstate="collapsed" desc="打包">
        return {
            'pokemon_name': self.pokemon_name,
            'dex_number': self.dex_number,
            'source': 'TUTORIAL',
            'data': self.per_generation_data,
            'form': self.pokemon_form
        }
        # </editor-fold>

    def pack_debug_print_data(self):
        # <editor-fold defaultstate="collapsed" desc="打包并输出">
        print('    - 宝可梦', self.pokemon_name)
        print('    - 图鉴ID', self.dex_number)
        print('    - 形态', self.pokemon_form)
        print('    - 学习方式', '传授')
        print('    - 解析后的数据', self.per_generation_data)
        for (idx, data_item) in enumerate(self.per_generation_data):
            if data_item:
                print("      - 可以在", tutorial_all_game_list[idx], '学习')
        return self.pack()
        # </editor-fold>

    def insert_database(self, connection: Connection):
        # <editor-fold defaultstate="collapsed" desc="插入数据库">
        """
        将数据插入数据库
        :param pokemon_id: 宝可梦详情表的ID
        :param connection:
        :return:
        """
        insert_into_values = [
            self.__move_id, self.dex_number, self.pokemon_form
        ]
        for item in self.per_generation_data:
            insert_into_values.append(item)
        try:
            print('插入教授招式', insert_into_values)
            connection.execute(
                'INSERT INTO pokemon_move_teach('
                'move_id, dex_number, form_name,'
                'crystal, fire_red_leaf_green, emerald, diamond_pearl, platinum, '
                'heart_gold_soul_silver, black_white, black_white_2, '
                'x_y, omega_ruby_alpha_sapphire, sun_moon, ultra_sun_ultra_moon, '
                'lets_go, shield_sword, brilliant_diamond_shining_pearl, legends_arceus) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                insert_into_values
            )
            connection.commit()
        except sqlite3.ProgrammingError:
            print("Programming Error", "Value is", insert_into_values)
            raise sqlite3.ProgrammingError
        # </editor-fold>


class MoveListRowParser:
    __input_row_data: list
    __middle_addition_dict: dict
    __middle_default: list
    learn_type: str  # LEVEL, TM, BREED
    dex_number: int
    pokemon_name: str
    form_name: str | None
    final_data: list
    special_info_dict: dict
    special_game_dict: dict

    def __inner_determine_delete_column(self, column: str):
        if column.__contains__('='):
            [column_equal_left, column_equal_right] = column.split('=')
            if column_equal_left in ['alt', 'note', 'gender', 'except', 'lt', 'gen', 'v']:
                self.special_info_dict[column_equal_left] = column_equal_right
            elif column_equal_left == 'form':
                self.form_name = column_equal_right
            elif column_equal_left.isdigit():
                column_game_index = int(column_equal_left) - 1
                self.special_game_dict[GAME_FULL_LIST[column_game_index]] = column_equal_right
            else:
                self.special_game_dict[column_equal_left] = column_equal_right
            return True
        else:
            return False

    def __init__(self, move_row: list[str]):
        """
        {{Movelist/level/gen1|105|嘎啦嘎啦|form=阿罗拉|火|幽灵|||||||33|LPLE=36|54}}
        {{Movelist/level/gen1|124|迷唇姐|冰|超能力|47||||}}
        :param move_row:
        """
        self.special_info_dict = {
            'gen': None,
            'note': None,
            'gender': None,
            'except': None,
        }
        self.__middle_addition_dict = {}
        self.form_name = None
        self.__middle_generation_data = [None] * generation_count
        self.special_game_dict = {}
        self.final_data = [None] * MOVE_LEARN_GAME_LIST.__len__()

        print(f'{PRINT_PREFIX_DEBUG}  - [DEBUG]', '整理前的行', f'{move_row}{PRINT_SUFFIX}')
        move_row = [column for column in move_row if not self.__inner_determine_delete_column(column)]
        print(f'{PRINT_PREFIX_DEBUG}  - [DEBUG]', '整理后的行', f'{move_row}{PRINT_SUFFIX}')
        self.__input_row_data = move_row
        split_first_column = move_row[0].split('/')
        self.learn_type = split_first_column[1]  # 学习的方式
        self.dex_number = int(move_row[1].strip('#'))  # 宝可梦图鉴编号
        self.pokemon_name = move_row[2]
        if split_first_column[2] == 'all':
            insert_start_index = 1
        else:
            insert_start_index = int(split_first_column[2].strip('gen'))
        print(f'{PRINT_PREFIX_DEBUG}    - [DEBUG]', '技能加入的世代', f'{insert_start_index + 1}{PRINT_SUFFIX}')
        for (idx, column) in enumerate(move_row[5:]):
            # 只保存不为空的值
            if column.strip() != '' and (idx + insert_start_index - 1) < self.__middle_generation_data.__len__():
                self.__middle_generation_data[idx + insert_start_index - 1] = column
        print(f'{PRINT_PREFIX_DEBUG}    - [DEBUG]', '每个世代', f'{self.__middle_generation_data}{PRINT_SUFFIX}')
        print(f'{PRINT_PREFIX_DEBUG}    - [DEBUG]', '特殊版本', f'{self.special_game_dict}{PRINT_SUFFIX}')
        for (generation_idx, generation_data) in enumerate(self.__middle_generation_data):  # 遍历每个世代
            if generation_data is not None:
                for game_key in MOVE_LEARN_GENERATION_DEFAULT_GAME[generation_idx]:  # 设置每个世代的默认值
                    self.final_data[MOVE_LEARN_GAME_LIST.index(game_key)] = generation_data.strip(',')
        for (special_game_key, special_game_value) in self.special_game_dict.items():
            if special_game_key == 'ORSA':
                special_game_key = 'ORAS'
            if special_game_key == 'PtHGSS':
                self.final_data[MOVE_LEARN_GAME_LIST.index('Pt')] = special_game_value
                self.final_data[MOVE_LEARN_GAME_LIST.index('HGSS')] = special_game_value
            else:
                self.final_data[MOVE_LEARN_GAME_LIST.index(special_game_key)] = special_game_value

    def print_debug_info(self):
        print('    - 学习方式', self.learn_type)
        print('    - 宝可梦', self.dex_number)
        print('    - 图鉴编号', self.dex_number)
        print('    - 形态', self.form_name)
        for (idx, temp_final_data) in enumerate(self.final_data):
            if temp_final_data is not None:
                print('      - 作品', MOVE_LEARN_GAME_LIST[idx], '数据', temp_final_data)
        print()
        return self

    def generate_insert_params(self, connection: Connection, move_id: int):
        """
        生成用于插入数据库的参数数组
        :param connection: 数据库连接
        :param move_id: 技能的ID
        :return:
        """
        # <editor-fold defaultstate="collapsed" desc="生成用于插入数据库的参数数组（函数体）">
        result = [move_id, self.dex_number, self.form_name, MOVE_LEARN_TYPE[self.learn_type]]
        for temp in self.final_data:
            result.append(temp)
        result.append(self.special_info_dict['gender'])
        result.append(self.special_info_dict['gen'])
        result.append(self.special_info_dict['note'])
        result.append(self.special_info_dict['except'])
        return result
        # </editor-fold>

    # <editor-fold defaultstate="collapsed" desc="Function 插入数据库">
    def insert_data(self, connection: Connection, move_id: int):
        connection.execute(
            'INSERT INTO pokemon_move_learn('
            'move_id, dex_number, form_name, pattern, '
            'red_green_blue, yellow, gold_silver, crystal, '
            'ruby_sapphire_emerald, fire_red_leaf_green, '
            'diamond_pearl, platinum, heart_green_soul_silver, '
            'black_white, black_white_2, '
            'x_y, omega_ruby_alpha_sapphire, '
            'sun_moon, ultra_sun_ultra_moon, lets_go, '
            'sword_shield, brilliant_diamond_shinning_pearl, legend_arceus, '
            'additional_gender, additional_generation, additional_note, additional_except) '
            'VALUES ('
            '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            self.generate_insert_params(connection, move_id)
        )
        connection.commit()
    # </editor-fold>

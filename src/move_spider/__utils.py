from sqlite3 import Connection

from src.constants import SELECT_POKEMON_DETAIL_ID_FIX


def create_move_basic_table(connection: Connection):
    """
    创建技能基本信息表格
    """
    # <editor-fold defaultstate="collapsed" desc="创建技能基本信息数据库">
    connection.execute(
        'DROP TABLE IF EXISTS pokemon_move_basic'
    )
    connection.execute(
        'CREATE TABLE pokemon_move_basic('
        '   id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
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
    connection.executescript(
        'CREATE INDEX idx__move_basic__move_id'
        '   ON pokemon_move_basic(move_id);'
        'CREATE INDEX idx__move_basic__name'
        '   ON pokemon_move_basic(name);'
        'CREATE INDEX idx__move_basic__damage_category'
        '   ON pokemon_move_basic(damage_category);'
        'CREATE INDEX idx__move_basic__move_type'
        '   ON pokemon_move_basic(type);'
    )
    connection.commit()
    # </editor-fold>


def create_move_teach_table(connection: Connection):
    """
    创建 教授招式 数据库
    :param connection:
    :return:
    """
    table_name = 'pokemon_move_teach'
    # <editor-fold defaultstate="collapsed" desc="创建宝可梦技能教授数据库">
    connection.execute(
        f'DROP TABLE IF EXISTS {table_name}'
    )
    connection.execute(
        f'CREATE TABLE {table_name}('
        f'  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
        f'  move_id INTEGER NOT NULL,'
        f'  dex_number INTEGER NOT NULL,'
        f'  form_name TEXT,'
        f'  crystal INTEGER,'
        f'  fire_red_leaf_green INTEGER,'
        f'  emerald INTEGER,'
        f'  diamond_pearl INTEGER,'
        f'  platinum INTEGER,'
        f'  heart_gold_soul_silver INTEGER,'
        f'  black_white INTEGER,'
        f'  black_white_2 INTEGER,'
        f'  x_y INTEGER,'
        f'  omega_ruby_alpha_sapphire INTEGER,'
        f'  sun_moon INTEGER,'
        f'  ultra_sun_ultra_moon INTEGER,'
        f'  lets_go INTEGER,'
        f'  shield_sword INTEGER,'
        f'  brilliant_diamond_shining_pearl INTEGER,'
        f'  legends_arceus INTEGER'
        f')'
    )
    connection.executescript(
        f'CREATE INDEX idx__{table_name}__move_id'
        f'   ON {table_name}(move_id);'
        f'CREATE INDEX idx__{table_name}__pokemon_id'
        f'   ON {table_name}(dex_number)'
    )
    connection.commit()
    # </editor-fold>


def create_move_learn_table(connection: Connection):
    """
    创建 等级提升，技能机器，遗传 数据表
    :param connection:
    :return:
    """
    table_name = 'pokemon_move_learn'
    # <editor-fold defaultstate="collapsed" desc="创建宝可梦技能学习数据库">
    connection.execute(
        f'DROP TABLE IF EXISTS {table_name}'
    )
    connection.execute(
        f'CREATE TABLE {table_name}('
        f'  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
        f'  move_id INTEGER NOT NULL,'
        f'  dex_number INTEGER NOT NULL,'
        f'  form_name TEXT,'
        f'  pattern INTEGER NOT NULL,'
        f'  red_green_blue TEXT,'
        f'  yellow TEXT,'
        f'  gold_silver TEXT,'
        f'  crystal TEXT,'
        f'  ruby_sapphire_emerald TEXT,'
        f'  fire_red_leaf_green TEXT,'
        f'  diamond_pearl TEXT,'
        f'  platinum TEXT,'
        f'  heart_green_soul_silver TEXT,'
        f'  black_white TEXT,'
        f'  black_white_2 TEXT,'
        f'  x_y TEXT,'
        f'  omega_ruby_alpha_sapphire TEXT,'
        f'  sun_moon TEXT,'
        f'  ultra_sun_ultra_moon TEXT,'
        f'  lets_go TEXT,'
        f'  sword_shield TEXT,'
        f'  brilliant_diamond_shinning_pearl TEXT,'
        f'  legend_arceus TEXT,'
        f'  additional_gender TEXT,'
        f'  additional_note TEXT,'
        f'  additional_generation TEXT,'
        f'  additional_except TEXT'
        f')'
    )
    connection.commit()
    # </editor-fold>


def select_move_id(move_name: str, connection: Connection):
    """
    根据技能名字寻找技能ID
    :param move_name: 技能名
    :param connection: 数据库连接
    :return:
    """
    # <editor-fold defaultstate="collapsed" desc="函数体">
    # print("[DEBUG][SQLITE]", '查找技能 名字为', move_name)
    cursor = connection.execute(
        'SELECT id FROM pokemon_move '
        'WHERE name = ?',
        [move_name]
    )
    selected = cursor.fetchone()
    if selected is None:
        raise Exception("Move can't Found")
    else:
        return selected[0]
    # </editor-fold>


def insert_basic_info(connection: Connection, input_array: list):
    connection.execute(
        'INSERT INTO pokemon_move_basic('
        'move_id, name, jp_name, en_name, '
        'type, damage_category, '
        'pp, power, accuracy, generation, '
        'touches, protect, magic_coat, snatch, mirror_move, kings_rock, sound, '
        'target) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        input_array
    )

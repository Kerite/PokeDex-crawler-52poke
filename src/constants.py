generation_count = 8

"""
https://wiki.52poke.com/wiki/Template:Learnset/tutorall
"""
GAME_FULL_LIST = [
    'RGB', 'Y', 'GS', 'C', 'RS', 'FRLG', 'E', 'DP', 'Pt', 'HGSS', 'BW', 'B2W2',
    'XY', 'ORAS', 'SM', 'USUM', 'LPLE', 'SWSH', 'BDSP', 'LA'
]
tutorial_all_game_list = [
    'C', 'FRLG', 'E', 'DP', 'Pt', 'HGSS', 'BW', 'B2W2',
    'XY', 'ORAS', 'SM', 'USUM', 'LPLE', 'SWSH', 'BDSP', 'LA'
]
TUTORIAL_ALL_GAME_LIST_CN = [
    '水晶', '火红叶绿', '绿宝石', '珍珠钻石', '白金', '心金魂银', '黑白', '黑2白2',
    'XY', '宝石复刻', '日月', '究极日月', '去吧皮卡丘/去吧伊布', '剑盾', '珍钻', '传说阿尔宙斯'
]

MOVE_LIST_ROW_TYPE = {
    'level': 'LEVEL',
    'tm': 'TM',
    'breed': 'BREED',
}

MOVE_LIST_GAME_CODE_TO_GENERATION = {
    'Y': 0,
    'C': 1,
    'FRLG': 2,
    'HGSS': 3,
    'PtHGSS': 3,
    'B2W2': 4,
    'ORAS': 5,
    'USUM': 6,
    'LPLE': 6,
}

SELECT_POKEMON_DETAIL_ID_FIX = {
    386: {
        '一般形态': '普通形态'
    },
    492: {
        '陆地': '陆上形态'
    }
}

"""
对应表是 pokemon_move_learn
"""
MOVE_LEARN_GAME_LIST = [
    'RGB', 'Y', 'GS', 'C', 'RSE', 'FRLG', 'DP', 'Pt', 'HGSS', 'BW', 'B2W2',
    'XY', 'ORAS', 'SM', 'USUM', 'LPLE', 'SWSH', 'BDSP', 'LA'
]
MOVE_LEARN_GAME_LENGTH = MOVE_LEARN_GAME_LIST.__len__()

MOVE_LEARN_GENERATION = [
    ['RGB', 'Y'], ['GS', 'C'], ['RSE', 'FRLG'], ['DP', 'Pt', 'HGSS'],
    ['BW', 'B2W2'], ['XY', 'ORAS'], ['SM', 'USUM', 'LPLE'],
    ['SWSH', 'BDSP', 'LA']
]
# 没有特殊值时每个世代的游戏列表
MOVE_LEARN_GENERATION_DEFAULT_GAME = [
    ['RGB', 'Y'], ['GS', 'C'], ['RSE', 'FRLG'], ['DP', 'Pt', 'HGSS'],
    ['BW', 'B2W2'], ['XY', 'ORAS'], ['SM', 'USUM'],
    ['SWSH']
]

MOVE_LEARN_TYPE = {
    'level': 'LEVEL',
    'tm': 'MOVE_MACHINE',
    'breed': 'BREED'
}

PRINT_PREFIX_HEADLINE = '\033[1;35m'
PRINT_PREFIX_DATABASE = '\033[1;36m'
PRINT_PREFIX_DEBUG = '\033[1;32m'
PRINT_SUFFIX = '\033[0m'

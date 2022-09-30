import csv

import re

import src.constants
from src import utils, value_map_dict, constants

# 体型（在X/Y和宝石复刻有变动（精灵））
body_name_list = [
    '球形', '蛇形', '鱼形', '双手形', '柱形', '双足兽形', '双腿形',
    '四足兽形', '双翅形', '触手形', '组合形', '人形', '多翅形', '虫形', '未知'
]
body_code_list = [
    'BALL', 'SNAKE', 'FISH', 'DUAL_HANDS', 'PILLAR', 'DUAL_FOOTS_MONSTER', 'DUAL_LEGS',
    'QUADRUPLE_FOOTS_MONSTER', 'DUAL_WINGS', 'TENTACLE', 'BUNDLE', 'HUMAN', 'MULTI_WINGS', 'BUG',
    'UNKNOWN'
]
key_suffix_list = ['', '2', '3', '4', '5', '6']
key_suffix_with_minus_list = ['', '-2', '-3', '-4', '-5', '-6']


def parse_pokemon_list(start_dex_number: int):
    latest_dex_number = 0
    with open('output_csv/pokemon_detail.csv', 'w', newline='', encoding='UTF-8') as csv_output:
        with open('output_csv/pokemon_list.csv', encoding='UTF-8') as csvfile:
            pokemon_reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            pokemon_writer = csv.writer(csv_output, quoting=csv.QUOTE_NONNUMERIC)
            pokemon_writer.writerow(['dex_number', 'name', 'jp_name', 'en_name', 'form_name',
                                     'height', 'weight',
                                     'type_1', 'type_2',
                                     'body', 'catch_rate', 'specie',
                                     'ability_1', 'ability_2', 'ability_hidden',
                                     'ev_hp', 'ev_attack', 'ev_defence',
                                     'ev_special_attack', 'ev_special_defence', 'ev_speed',
                                     'exp_yield', 'exp_yield_gen_5', 'exp_lv_100',
                                     'egg_group_1', 'egg_group_2', 'egg_cycle',
                                     'hp', 'attack', 'defence', 'special_attack', 'special_defence', 'speed'])
            for (pokemon_dex_number, pokemon_dex_name, pokemon_form, pokemon_type_1, pokemon_type_2, pokemon_generation,
                 pokemon_icon_row, pokemon_icon_column, pokemon_detail) in pokemon_reader:
                if pokemon_dex_number == latest_dex_number:
                    continue
                pokemon_detail_dic: dict = eval(pokemon_detail)
                pokemon_basic_info_dic = pokemon_detail_dic['basic_info']
                print('====================================')
                print('宝可梦', pokemon_dex_name)
                # 名字的key: jname(日文名字) enname(英文名字)
                jp_name = pokemon_basic_info_dic['jname']
                en_name = pokemon_basic_info_dic['enname']
                height_list = parse_key(pokemon_basic_info_dic, 'height')
                weight_list = parse_key(pokemon_basic_info_dic, 'weight')

                # ======形态======
                # 形态的key: form1(形态1) form2(形态2)  -----(当只有一个形态时不存在)
                form_names = []
                for i in range(1, 7):
                    key_str = 'form' + i.__str__()
                    if key_str not in pokemon_basic_info_dic:
                        form_names.append(None)
                    else:
                        form_names.append(pokemon_basic_info_dic[key_str])
                print("宝可梦的形态：", form_names)

                # ======属性======
                # 属性的key: typen type1 type2
                type_n_list = parse_key(pokemon_basic_info_dic, 'typen')
                type_1_list = parse_key(pokemon_basic_info_dic, 'type1', suffix_array=key_suffix_with_minus_list,
                                        merge_first=False)
                type_2_list = parse_key(pokemon_basic_info_dic, 'type2', suffix_array=key_suffix_with_minus_list,
                                        merge_first=False)
                print('属性(n,1,2)', type_n_list, type_1_list, type_2_list)
                for idx, type_count_str in enumerate(type_n_list):
                    if type_count_str is None:
                        type_count_str = '2'
                    type_count = int(type_count_str)
                    if type_1_list[idx] is None:
                        type_1_list[idx] = type_1_list[0]
                    if (type_2_list[idx] is None) & (type_count == 2):
                        type_2_list[idx] = type_2_list[0]

                # ======捕获率======
                # 基础信息key: catchrate(捕获率) body(体型)
                # ----  6：双足兽形
                body_list = parse_key(pokemon_basic_info_dic, 'body')
                catch_rate_list = parse_key(pokemon_basic_info_dic, 'catchrate')
                if catch_rate_list[1] == '':
                    catch_rate_list[1] = catch_rate_list[0]
                print('捕获率', catch_rate_list)

                # ======分类======
                # 分类的key: species(分类 形态1) species2(分类 形态2)
                specie_list = parse_key(pokemon_basic_info_dic, 'species')

                # 计算宝可梦总共有多少个形态
                while None in form_names:
                    form_names.remove(None)
                if len(form_names) == 0:
                    form_names = [None]

                # ======特性======
                # 特性的key: abilityn(特性数量) abilityn2(形态2特性数量)
                #   ability1(形态1特性1) ability2(形态1特性2) abilityd(隐藏特性)
                #   ability1-2(特性1形态2) ability2-2(特性2形态1) abilityd2(隐藏特性形态2)
                abilityn_list = parse_key(pokemon_basic_info_dic, 'abilityn', merge_first=False)
                ability1_list = parse_key(pokemon_basic_info_dic, 'ability1', key_suffix_with_minus_list)
                ability2_list = parse_key(pokemon_basic_info_dic, 'ability2', key_suffix_with_minus_list,
                                          merge_first=False)
                ability_hidden_list = parse_key(pokemon_basic_info_dic, 'abilityd',
                                                merge_first=False)
                print('特性(处理前)', abilityn_list, ability1_list, ability2_list, ability_hidden_list)
                for idx, abilityn_str in enumerate(abilityn_list):
                    if (abilityn_str is None) or (abilityn_str == ''):
                        abilityn_str = '1'
                    ability_count = int(abilityn_str)
                    if (ability2_list[idx] is None) and (ability_count > 1):
                        ability2_list[idx] = ability2_list[0]
                print('特性(处理后)', abilityn_list, ability1_list, ability2_list, ability_hidden_list)

                # 图鉴编号key: ndex(全国图鉴) kdex(关都图鉴) oldjdex(城都 金银) jdex(城都 心金魂银)
                #   宝石: oldhdex(丰缘图鉴 宝石) hdex(丰缘图鉴 宝石复刻)
                #   DP:  sdex(神奥图鉴)
                #   BW:  idex(合众图鉴 黑白) idex2(合众图鉴 黑白2)
                #   X/Y: kdexs(卡洛斯图鉴 中央地区)
                #   adex(阿罗拉图鉴 日月) adexa(阿卡拉 日月) adexu(乌拉乌拉 日月) adexp(波尼 日月)
                #   adex2(阿罗拉图鉴 究极日月) adexa2(阿卡拉 究极日月) adexu2(乌拉乌拉 究极日月) adexp(波尼 究极日月)
                #   gdex(伽勒尔图鉴) hidex(洗翠图鉴)
                # 身形的key: height(身高) weight(体重) height2(身高 形态2) gendercode(性别分布) color(图鉴颜色)
                #         性别code：127(1:1)

                # ======生蛋相关======
                # 蛋组的key: egggroupn(蛋组数量) egggroup1(蛋组) eggcycles(孵化周期)
                egg_group_n_list = parse_key(pokemon_basic_info_dic, 'egggroupn')
                egg_group_1_list = parse_key(pokemon_basic_info_dic, 'egggroup1', key_suffix_with_minus_list)
                egg_group_2_list = parse_key(pokemon_basic_info_dic, 'egggroup2', key_suffix_with_minus_list,
                                             merge_first=False)
                egg_cycle_list = parse_key(pokemon_basic_info_dic, 'eggcycles')
                print("生蛋相关", "蛋组", egg_group_n_list, egg_group_1_list, egg_group_2_list)
                for idx, egg_group_count_str in enumerate(egg_group_n_list):
                    egg_group_count = int(egg_group_count_str)
                    if (egg_group_count == 2) & (egg_group_2_list[idx] is None):
                        egg_group_2_list[idx] = egg_group_2_list[0]

                # ======努力值======
                # 努力值key: expyield(基础经验值) lv100exp(100级经验值) evhp(HP努力值) evat(攻击努力值) evde(防御努力值)
                #   evsa(特攻努力值) evsd(特防努力值) evsp(速度努力值)
                exp_yield_list = parse_key(pokemon_basic_info_dic, 'expyield')
                exp_yield_gen5_list = parse_key(pokemon_basic_info_dic, 'expyieldgen5', key_suffix_with_minus_list,
                                                merge_first=False)
                lv_100_exp_list = parse_key(pokemon_basic_info_dic, 'lv100exp')
                ev_hp_list = parse_key(pokemon_basic_info_dic, 'evhp', default_value='0')
                ev_at_list = parse_key(pokemon_basic_info_dic, 'evat', default_value='0')
                ev_de_list = parse_key(pokemon_basic_info_dic, 'evde', default_value='0')
                ev_sa_list = parse_key(pokemon_basic_info_dic, 'evsa', default_value='0')
                ev_sd_list = parse_key(pokemon_basic_info_dic, 'evsd', default_value='0')
                ev_sp_list = parse_key(pokemon_basic_info_dic, 'evsp', default_value='0')

                # ======种族值======
                species_strength_list = pokemon_detail_dic['pokemon_details_species_strength']
                species_strength_dic = {}
                for species_strength_item in species_strength_list:
                    form_name = '一般的样子'
                    if 'form_name' in species_strength_item:
                        form_name = species_strength_item['form_name']
                    species_strength_dic[form_name] = [
                        int(species_strength_item['hp']), int(species_strength_item['atk']),
                        int(species_strength_item['def']), int(species_strength_item['spa']),
                        int(species_strength_item['spd']), int(species_strength_item['speed'])
                    ]
                print('种族值字典', species_strength_dic)

                # ======宝可梦图像======
                image_code_list = parse_key(pokemon_basic_info_dic, 'imagecode', merge_first=False)
                image_list = parse_key(pokemon_basic_info_dic, 'image', merge_first=False)

                # ======存到csv中======
                for i, form_name in enumerate(form_names):
                    if (pokemon_dex_number == 718) and ((form_name == '细胞') or (form_name == '核心')):
                        continue
                    species_strength = utils.get_specie_strength(
                        species_strength_dic, pokemon_dex_name, form_name
                    )

                    body_idx = 14
                    if body_list[i] != '':
                        body_idx = int(body_list[i]) - 1

                    saved_image_name = int(pokemon_dex_number).__str__() + '#' + pokemon_dex_name + '#'
                    if form_name is not None:
                        saved_image_name = saved_image_name + form_name + "#"
                    if pokemon_dex_number >= start_dex_number:
                        if image_code_list[i] is None and image_list[i] is None:
                            process_image(None, int(pokemon_dex_number).__str__().zfill(3) + en_name + '.png',
                                          saved_image_name)
                        else:
                            process_image(image_code_list[i], image_list[i], saved_image_name)

                    data = [int(pokemon_dex_number), pokemon_dex_name, jp_name, en_name, form_names[i],
                            height_list[i], weight_list[i],
                            value_map_dict.pokemon_types[type_1_list[i]], value_map_dict.pokemon_types[type_2_list[i]],
                            body_code_list[body_idx], catch_rate_list[i], specie_list[i],
                            # 特性
                            ability1_list[i], ability2_list[i], ability_hidden_list[i],
                            # 体力，攻击，防御，特攻，特防，速度
                            int(ev_hp_list[i].replace('}}', '')), int(ev_at_list[i].replace('}}', '')),
                            int(ev_de_list[i].replace('}}', '')), int(ev_sa_list[i].replace('}}', '')),
                            int(ev_sd_list[i].replace('}}', '')), int(ev_sp_list[i].replace('}}', '')),
                            # 对战获得经验值（分为五代前和五代后，为空则为不详）
                            exp_yield_list[i], exp_yield_gen5_list[i],
                            # 满级经验值
                            int(lv_100_exp_list[i].replace(',', '')),
                            # 蛋组
                            value_map_dict.egg_group_dict1[egg_group_1_list[i]],
                            value_map_dict.egg_group_dict2[egg_group_2_list[i]], egg_cycle_list[i],
                            # 种族值
                            species_strength, saved_image_name]
                    print(data)
                    pokemon_writer.writerow(utils.flat_list(data))
                    print()
                latest_dex_number = pokemon_dex_number


def parse_key(
        basic_info_dic: dict,
        key: str,
        suffix_array: list[str] = key_suffix_list,
        merge_first: bool = True,
        default_value=None
):
    result_array = []
    for i in suffix_array:
        if key + i not in basic_info_dic:
            if suffix_array.index(i) == 0:
                result_array.append(default_value)
            elif not merge_first:
                result_array.append(default_value)
            else:
                result_value = result_array[0]
                if isinstance(result_value, str):
                    result_value = result_value.strip()
                result_array.append(result_value)
        else:
            result_value = basic_info_dic[key + i].replace('&mdash;', '').replace('-->', '').replace('<!--', '')
            result_array.append(result_value.strip())
    return result_array


def process_image(image_code_str: str | None, image_str: str | None, saved_name: str):
    print(f"{src.constants.PRINT_PREFIX_DEBUG}Handling Image", image_code_str, image_str, 'To',
          f'{saved_name}{constants.PRINT_SUFFIX}')
    if image_str is not None:
        utils.download_media(image_str.replace(' ', '_'), saved_name)
    elif re.match(r'\[\[File:[\S ]*?\|[0-9]{1,9}px]]', image_code_str):
        image_code = re.findall(r'\[\[File:([\S ]*?)\|[0-9]{1,9}px]]', image_code_str)[0]
        utils.download_media(image_code.replace(' ', '_'), saved_name)
    else:
        print(f"[ERROR]Image Fallback", image_code_str, image_str)


if __name__ == '__main__':
    parse_pokemon_list(0)

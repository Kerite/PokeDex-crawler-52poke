class FormNotFoundError(Exception):
    pass


class SpecieStrengthAdditionalParser:
    __species_strength_dic: dict[str, list]
    __pokemon_dex_name: str
    __form_name: str | None
    result: list = None

    def __init__(self, species_strength_dic: dict, pokemon_dex_name: str, form_name: str | None):
        self.__species_strength_dic = species_strength_dic
        self.__pokemon_dex_name = pokemon_dex_name
        self.__form_name = form_name

        if form_name is None:
            if pokemon_dex_name in species_strength_dic:
                self.result = species_strength_dic[pokemon_dex_name]
            else:
                self.__fallback_find()
        else:
            from src.value_map_dict import special_pokemon_form_name_map
            if form_name in species_strength_dic:
                self.result = species_strength_dic[form_name]
            elif pokemon_dex_name in special_pokemon_form_name_map and \
                    form_name in special_pokemon_form_name_map[pokemon_dex_name]:
                # 特殊情况，在预定义的特殊表中搜索
                self.result = species_strength_dic[special_pokemon_form_name_map[pokemon_dex_name][form_name]]
            elif form_name == pokemon_dex_name:
                # 形态和图鉴名字相同（基本形态）
                self.__fallback_find()
            elif form_name.__contains__('超极巨化'):
                if '一般' in species_strength_dic:
                    self.result = species_strength_dic['一般']
                else:
                    self.result = species_strength_dic['一般的样子']
            elif form_name.__contains__('超级'):
                result = species_strength_dic['超级进化']
            else:
                self.__fallback_find()

    def __fallback_find(self):
        """
        在 第六世代起 第七世代起 第七世代起 一般 一般的样子 中搜索是否存在指定的key
        :return: Nothing
        """
        for judge_key in ['第六世代起', '第七世代起', '一般', '一般的样子']:
            if judge_key in self.species_strength_dic:
                self.result = self.species_strength_dic[judge_key]
        if self.result is None:
            raise FormNotFoundError

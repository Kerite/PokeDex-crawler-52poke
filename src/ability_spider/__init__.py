from pokemon_ability import PokemonAbilitySpider
from src.utils import default_sqlite_path

if __name__ == '__main__':
    PokemonAbilitySpider(output_path=default_sqlite_path) \
        .fetch_pokemon_ability_list()

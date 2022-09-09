import concurrent.futures

import requests
from bs4 import BeautifulSoup


def save_pokemon(pokemon_id):
    pokemon_num_str = pokemon_id.__str__().zfill(3)
    r = requests.get("https://www.pokemon.cn/play/pokedex/" + pokemon_num_str)
    soup = BeautifulSoup(r.text, features="html.parser")

    img_url = soup.find("img", "pokemon-img__front").attrs['src']
    img = requests.get("https://www.pokemon.cn" + img_url)

    pokemon_name = soup.find("p", "pokemon-slider__main-name").string
    saved_file_name = pokemon_num_str + '#' + pokemon_name

    pokemon_sub_name = soup.find("p", "pokemon-slider__main-subname").string
    if pokemon_sub_name is not None:
        saved_file_name = saved_file_name + "#" + pokemon_sub_name.replace("/", "#")

    file = open('imgs/' + saved_file_name + '.png', 'ab')
    print("正在保存 " + saved_file_name)
    file.write(img.content)
    file.close()

    if "_" not in pokemon_num_str:
        style_boxes = soup.find_all("div", "pokemon-style-box")
        for style_box in style_boxes:
            style_pokemon_url = style_box.a.attrs['href']
            if "_" in style_pokemon_url:
                style_pokemon_id = style_pokemon_url.split("/")[3]
                save_pokemon(style_pokemon_id)


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(15) as executor:
        executor.map(save_pokemon, range(1, 898))
    print("保存完毕")

import csv
import requests
from bs4 import BeautifulSoup

proxies = {
    'http': '127.0.0.1:7890',
    'https': '127.0.0.1:7890'
}


def main():
    r = requests.get("https://wiki.52poke.com/zh-hans/%E6%8B%9B%E5%BC%8F%E5%88%97%E8%A1%A8", proxies=proxies)
    soup = BeautifulSoup(r.text, features="html.parser")
    tables = soup.find_all("table", "hvlist")
    with open('skills.csv', 'w', newline='', encoding='UTF-8') as csv_file:
        skill_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        for skill_table in tables:
            skill_gen = skill_table.find_previous_sibling().span.attrs['id']
            skill_rows = skill_table.find_all("tr")
            for skill_row in skill_rows:
                tds = skill_row.find_all("td")
                if len(tds) > 0:
                    if tds[0].string is not None:
                        skill_id = tds[0].string.replace("\n", "")
                        skill_name = tds[1].a.string
                        if skill_name is None:
                            skill_name = tds[1].contents[1].string
                        skill_type = tds[4].string.replace("\n", "")
                        skill_damage = tds[5].a.string.replace("\n", "")
                        skill_power = tds[6].string.replace("\n", "")
                        skill_accuracy = tds[7].string.replace("\n", "")
                        skill_pp = tds[8].string.replace("\n", "")
                        skill_description = tds[9].string.replace("\n", "")
                        skill_writer.writerow([
                            skill_gen, skill_id, skill_name, skill_type, skill_damage, skill_power, skill_accuracy,
                            skill_pp, skill_description
                        ])
                        print(skill_gen, skill_id, skill_name,
                              "属性：" + skill_type + "，分类：" + skill_damage + "，威力：" + skill_power +
                              "，命中：" + skill_accuracy + "，PP:" + skill_pp, skill_description)


if __name__ == "__main__":
    main()

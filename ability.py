import csv
import requests
from bs4 import BeautifulSoup

proxies = {
    'http': '127.0.0.1:7890',
    'https': '127.0.0.1:7890'
}


def main():
    r = requests.get("https://wiki.52poke.com/zh-hans/%E7%89%B9%E6%80%A7%E5%88%97%E8%A1%A8", proxies=proxies)
    soup = BeautifulSoup(r.text, features="html.parser")
    tables = soup.find_all("table", "eplist")
    with open('ability.csv', 'w', newline='', encoding='UTF-8') as csv_file:
        ability_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        for ability_table in tables:
            # ability_gen = ability_table.find_previous_sibling().span.attrs['id']
            ability_rows = ability_table.find_all("tr")
            for ability_row in ability_rows:
                tds = ability_row.find_all("td")
                if len(tds) > 0:
                    # print(tds)
                    if tds[0].string is not None:
                        ability_id = tds[0].string.replace("\n", "")
                        ability_name = tds[1].a.string.replace("\n", "")
                        ability_description = tds[4].string.replace("\n", "")
                        ability_writer.writerow([ability_id, ability_name, ability_description])
                        print(ability_id, ability_name, ability_description)


if __name__ == "__main__":
    main()

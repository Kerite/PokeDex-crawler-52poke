import os
import sqlite3

if __name__ == '__main__':
    connection = sqlite3.connect(r"D:\Projects\AndroidProjects\PokeDex\app\src\main\assets\database\assets.db")
    cur = connection.cursor()

    cur.execute("DROP TABLE IF EXISTS images")
    cur.execute(
        """CREATE TABLE images(
id INTEGER PRIMARY KEY AUTOINCREMENT,
image_type TEXT NOT NULL,
image_key TEXT,
image_content BLOB
)""")
    connection.commit()

    for file in os.listdir("./small_icon"):
        with open("./small_icon/" + file, "rb") as input_file:
            _blob = input_file.read()
            cur.execute(
                "INSERT INTO images (image_type, image_key, image_content) VALUES ('small_icon', ?, ?)",
                [file.split(".")[0], sqlite3.Binary(_blob)]
            )
            connection.commit()

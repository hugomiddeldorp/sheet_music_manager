import json
import sqlite3


def main():
    conn = sqlite3.connect('lib.db')
    try:
        conn.execute("""CREATE VIRTUAL TABLE works
                USING FTS5(title, composer);""")
        print("Database created")
    except: pass

    with open("debussy.json", "r") as json_file:
        data = json.load(json_file)

    composer = data["composer"]["complete_name"]
    path  = "Aquanaut.pdf"
    for work in data["works"]:
        conn.execute("""INSERT INTO works (title, composer, path)
                VALUES (?, ?, ?)""", (work["title"], composer, path))
        print("Added {}".format(work["title"]))

    conn.commit()


if __name__ == "__main__":
    main()

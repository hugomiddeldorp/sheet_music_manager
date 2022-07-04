import json
import sqlite3


def main():
    conn = sqlite3.connect('lib.db')
    try:
        conn.execute("""CREATE VIRTUAL TABLE works
                USING FTS5(title, composer);""")
        print("Database created")
    except: pass

    with open("bach.json", "r") as json_file:
        data = json.load(json_file)

    composer = data["composer"]["complete_name"]
    for work in data["works"]:
        conn.execute("""INSERT INTO works (title, composer)
                VALUES (?, ?)""", (work["title"], composer))
        print("Added {}".format(work["title"]))

    conn.commit()


if __name__ == "__main__":
    main()

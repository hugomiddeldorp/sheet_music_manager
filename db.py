import sqlite3
import os


def init():
    global conn

    conn = sqlite3.connect('lib.db')
    try:
        conn.execute("""CREATE VIRTUAL TABLE works
                USING FTS5(title, composer);""")
        print("Database created")
    except:
#        conn.execute("""INSERT INTO WORKS (TITLE,COMPOSER)
#                VALUES ('Violin Partita No.2 in D minor, BWV 1004', 'Johann Sebastian Bach');""")
#        conn.execute("""INSERT INTO WORKS (TITLE,COMPOSER)
#                VALUES ('Piano Quintet in E flat major, op. 44', 'Robert Schumann');""")
#        conn.commit()
        pass


def close():
    conn.close()


def find(search):
    if len(search) > 0:
        search.replace(" ", "+")
        search += "*"

    try:
        results = conn.execute("""SELECT *
                FROM works
                WHERE works=?;""", (search,))
    except:
        results = conn.execute("""SELECT *
                FROM works""")
        
    results_array = []
    for work in results: results_array.append(work)
    return results_array


def update():
    path = os.getcwd()
    file_names = []

    for root, dirs, files in os.walk(path):
        for file in files:
            file_names.append(file)

    return file_names


if __name__ == "__main__":
    print(update())

import sqlite3
import os
import search


def init():
    global conn

    conn = sqlite3.connect('lib.db')
    try:
        conn.execute("""CREATE VIRTUAL TABLE works
                USING FTS5(title, composer, path);""")
        print("Database created")
    except:
        pass


def close():
    conn.close()


def findPath(query):
    results = conn.execute("""SELECT path
            FROM works
            WHERE path=?;""", (query,))

    results_array = []
    for work in results: results_array.append(work)
    return results_array


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


def getFileNames():
    path = os.getcwd()
    file_names = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".pdf"):
                file_names.append(file)

    return file_names


def addEntry(result, path):
    conn.execute("""INSERT INTO works
            VALUES (?, ?, ?)""", (result["title"], result["composer"], path))
    conn.commit()


def update():
    file_names = getFileNames()

    for file in file_names:
        if not findPath(file):
            print("New file found: ", file)
            result = search.search(file[:-4])
            if result == -1: 
                result = {"title": file[:-4], "composer": "unknown"}
            addEntry(result, file)


if __name__ == "__main__":
#    print(getFileNames())
    init()
    update()

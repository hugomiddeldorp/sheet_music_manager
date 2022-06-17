import curses
import sqlite3
from curses import wrapper


def dbStart():
    global conn

    conn = sqlite3.connect('library.db')
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


def displayResults(search):
    results_in.clear()

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

    i = 1
    for work in results:
        r = work[0] + " - " + work[1]
        if i == highlight + 1:
            results_in.addstr(i, 2, r, curses.A_REVERSE)
        else:
            results_in.addstr(i, 2, r)
        i += 1
    
    if i == 1:
        results_in.addstr(i, 2, "No results found.", curses.A_DIM)

    results_in.refresh()


def init():
    global screen, search_bar, results_out, results_in, num_rows, num_cols, buffer, highlight

    dbStart()
    screen = curses.initscr()
    num_rows, num_cols = screen.getmaxyx()
    search_bar = curses.newwin(1, num_cols, 1, 0)
    results_out = curses.newwin(num_rows - 3, num_cols, 3, 0)
    results_in = curses.newwin(num_rows - 5, num_cols - 2, 4, 1)
    buffer = ""
    highlight = 0

    curses.start_color()
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    screen.clear()

    screen.addstr(0, 0,
            " Sheet Music Manager v0.1 - by Hugo Middeldorp ",
            curses.A_BOLD | curses.A_REVERSE)
    screen.refresh()

    resetSearchBar()

    results_out.border()
    results_out.addstr(0, 0,
            " RESULTS ",
            curses.A_REVERSE)
    results_out.refresh()

    displayResults("")
    search_bar.move(0, 0)


def resetSearchBar():
    search_bar.clear()
    search_bar.addstr(0, 0,
            "Type to start searching...",
            curses.A_DIM)
    search_bar.refresh()
    screen.refresh()
    search_bar.move(0, 0)


def processKeyEvent():
    # TODO: need to handle when chars go over screen limit
    global buffer
    c = search_bar.getkey()

    if buffer == "":
        search_bar.clear()

    if c == "\n":
        if buffer == ":q":
            return False
        buffer = ""
        resetSearchBar()
    elif c == "KEY_RESIZE":
        num_rows, num_cols = screen.getmaxyx()
    elif c == "KEY_MOUSE" or c == "KEY_LEFT" or c == "KEY_RIGHT":
        pass
    elif c == "KEY_DOWN":
        highlight += 1
    elif c == "KEY_UP":
        highlight = min(0, highlight - 1)
    elif ord(c) == 127 or c == 'KEY_BACKSPACE' or c == '\x08':
        if len(buffer) > 0:
            search_bar.delch(0, len(buffer) - 1)
            buffer = buffer[:-1]
    elif c == "KEY_DC":
        pass
    else:
        buffer += c
        search_bar.addch(0, len(buffer) - 1, c)

    displayResults(buffer)

    return True
    


def kill():
    conn.close()
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()


def main(screen):
    # TODO: properly manage screen_resize
    init()

    while processKeyEvent():
        pass

    kill()


if __name__ == "__main__":
    wrapper(main)

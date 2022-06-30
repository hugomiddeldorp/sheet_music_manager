import sys
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


def find(search):
    global search_len
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
    search_len = len(results_array)
    return results_array


def displayResults(results):
    global num_rows, num_cols, highlight
    # TODO: Figure out a better way to handle highlight
    # and also think of how to handle when results go over page lim
    y_offst= 2 # From top of window
    screen_padding = 5 # From other lines on screen
    highlight = min(highlight, len(results))

    results_win.clear()
    results_win.border()
    results_win.addstr(0, 0,
            " RESULTS ",
            curses.A_REVERSE)

    y = 0
    for work in results[:num_rows - screen_padding]:
        r = work[0] + " - " + work[1] # Title - Composer
        if y == highlight:
            results_win.addstr(y + y_offst, 2, r, curses.A_REVERSE)
        else:
            results_win.addstr(y + y_offst, 2, r)
        y += 1
    
    if y == 0:
        results_win.addstr(y + y_offst, 2, "No results found.", curses.A_DIM)

    results_win.refresh()


def init():
    global screen, search_bar, results_win, num_rows, num_cols
    global buffer, highlight, search_len, buffer_offset

    dbStart()
    screen = curses.initscr()
    num_rows, num_cols = screen.getmaxyx()
    search_bar = curses.newwin(1, num_cols, 1, 0)
    results_win = curses.newwin(num_rows - 3, num_cols, 3, 0)
    buffer = ""
    highlight = 0
    search_len = 0
    buffer_offset = 0

    curses.start_color()
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)
    search_bar.keypad(True)

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    screen.clear()

    screen.addstr(0, 0,
            " Sheet Music Manager v0.1 - by Hugo Middeldorp ",
            curses.A_BOLD | curses.A_REVERSE)
    screen.refresh()

    resetSearchBar()

    displayResults(find(""))
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
    # TODO: add sideways movement
    global buffer, highlight, search_len, buffer_offset
    c = search_bar.getch()

    if buffer == "":
        search_bar.clear()

    if c == ord('\n'):
        if buffer == ":q":
            return False
        buffer = ""
        resetSearchBar()
    elif c == curses.KEY_RESIZE:
        num_rows, num_cols = screen.getmaxyx()
    elif c == curses.KEY_MOUSE or c == curses.KEY_LEFT or c == curses.KEY_RIGHT:
        pass
    elif c == curses.KEY_DOWN: 
        if highlight < search_len - 1: highlight += 1
    elif c == curses.KEY_UP:
        if highlight > 0:
            highlight -= 1
    elif c == curses.KEY_BACKSPACE:
        if len(buffer) > 0:
            search_bar.delch(0, len(buffer) - buffer_offset - 1)
            buffer = buffer[:-1]
            if buffer_offset:
                buffer_offset -= 1
                search_bar.addstr(0, 0, buffer[buffer_offset:])
    elif c == 27:
        buffer = ""
        resetSearchBar()
    else:
        buffer += chr(c)
        if len(buffer) >= search_bar.getmaxyx()[1]:
            search_bar.delch(0, 0)
            buffer_offset += 1
        search_bar.addch(0, len(buffer) - buffer_offset - 1, c)

    results = find(buffer)
    displayResults(results)

    return True
    


def kill():
    conn.close()
    curses.nocbreak()
    screen.keypad(False)
    search_bar.keypad(False)
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

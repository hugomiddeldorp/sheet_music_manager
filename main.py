import sys, os, subprocess
from subprocess import DEVNULL, STDOUT
from threading import Thread
import curses
import curses.ascii
import sqlite3
from curses import wrapper

import db

# TODO: Get rid of arbitrary numbers (eg. scr_y_padding);
#       they should be calculated automatically
# TODO: Use threading to scrape web?


def openResult(results, i):
    # TODO: Handle errors
    path = results[i][2]
    try:
        os.startfile(path)
    except:
        p = subprocess.Popen(["open", path], stdout=DEVNULL, stderr=STDOUT)


def displayResults(results):
    # TODO: Show more details with Ctrl-D ? To see filename
    global highlight, results_offset

    y_offst= 2 # From top of window
    scr_y_padding = 7 # From other rows on screen
    scr_x_padding = 4 # Other columns on screen

    results_win.erase()
    results_win.border()
    results_win.addstr(0, 0,
            " RESULTS ",
            curses.A_REVERSE)

    y = 0
    for work in results[results_offset:
                        results_offset + num_rows - scr_y_padding]:
        r = work[0] + " - " + work[1] # Title - Composer
        
        if len(r) >= num_cols - scr_x_padding:
            r = r[:num_cols - scr_x_padding - 3]
            r += "..."

        if y == highlight:
            results_win.addstr(y + y_offst, 2, r, curses.A_REVERSE)
        else:
            results_win.addstr(y + y_offst, 2, r)
        y += 1
    
    if y == 0:
        results_win.addstr(y + y_offst, 2, "No results found.", curses.A_DIM)

    results_win.refresh()


def init():
    global screen, search_bar, status_bar, results_win, num_rows, num_cols
    global buffer, highlight, search_len, buffer_offset, results_offset

    db.init()
    screen = curses.initscr()
    num_rows, num_cols = screen.getmaxyx()
    search_bar = curses.newwin(1, num_cols, 1, 0)
    results_win = curses.newwin(num_rows - 4, num_cols, 3, 0)
    status_bar = curses.newwin(1, num_cols, num_rows - 1, 0)
    buffer = ""
    highlight = 0
    buffer_offset = 0
    results_offset = 0

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

    updateStatus()
    resetSearchBar()

    results = db.find("")
    search_len = len(results)
    displayResults(results)
    search_bar.move(0, 0)


def resetSearchBar():
    search_bar.erase()
    search_bar.addstr(0, 0,
            "Type to start searching...",
            curses.A_DIM)
    search_bar.refresh()
    screen.refresh()
    search_bar.move(0, 0)


def updateStatus(status=":q to Quit | :u to Update library"):
    status_bar.erase()
    status_bar.addstr(0, 0, status, curses.A_ITALIC)
    status_bar.refresh()
    screen.refresh()


def screenResize():
    global num_rows, num_cols

    num_rows, num_cols = screen.getmaxyx()

    screen.resize(num_rows, num_cols)
    search_bar.resize(1, num_cols)
    status_bar.resize(1, num_cols)
    results_win.resize(num_rows - 4, num_cols)
    
    screen.clear()
    search_bar.clear()
    status_bar.clear()
    results_win.clear()

    screen.addstr(0, 0,
            " Sheet Music Manager v0.1 - by Hugo Middeldorp ",
            curses.A_BOLD | curses.A_REVERSE)
    resetSearchBar()
    screen.refresh()

    search_bar.move(0, 0)


def updateLibrary():
    screen.nodelay(True)
    file_names = db.getFileNames()
    percent = 0
    i = 0
    for file in file_names:
        char = screen.getch()
        if char == ord("c"):
            updateStatus("Update cancelled, {}% complete".format(percent))
            break
        db.update(file)
        i += 1
        percent = int(i/len(file_names) * 100)
        status = "["
        for j in range(0, 40):
            if i / len(file_names) <= j / 40:
                status += "."
            else: status += "#"
        status += "] {}% | Press C to cancel".format(percent)
        updateStatus(status)
    screen.nodelay(False)


def editEntry(results, i):
    curses.echo()
    status_title = "Title: "
    updateStatus(status_title)
    title = status_bar.getstr(0, len(status_title))
    status_composer = "Composer: "
    updateStatus(status_composer)
    composer = status_bar.getstr(0, len(status_composer))
    curses.noecho()

    path = results[i][2]
    updates = {"title": title.decode("utf-8"), "composer": composer.decode("utf-8")}
    db.editEntry(path, updates)


def processKeyEvent():
    # TODO: add sideways movement
    # TODO: remove entry from db - how to handle?
    global buffer, highlight, search_len, buffer_offset, results_offset
    global num_rows
    c = search_bar.getch()

    if buffer == "":
        search_bar.erase()

    if c == ord('\n'):
        if buffer == ":q":
            return False
        elif buffer == ":u":
            updateLibrary()
        else:
            results = db.find(buffer)
            search_len = len(results)
            openResult(results, highlight + results_offset)
        buffer = ""
        resetSearchBar()
    elif c == curses.KEY_RESIZE:
        # TODO: don't reset search after resizing
        screenResize()
        buffer = ""
    elif c == curses.KEY_MOUSE or c == curses.KEY_LEFT or c == curses.KEY_RIGHT:
        pass
    elif curses.ascii.unctrl(c) == "^E":
        results = db.find(buffer)
        search_len = len(results)
        editEntry(results, highlight + results_offset)
    elif c == curses.KEY_DOWN: 
        # TODO: ERROR Type text and use arrows,
        #       the cursor goes down to last result
        if highlight < search_len - results_offset - 1:
            if highlight >= num_rows - 8:
                results_offset += 1
            else: highlight += 1
    elif c == curses.KEY_UP:
        if highlight > 0: 
            highlight -= 1
        elif results_offset > 0:
            results_offset -= 1
    elif c == curses.KEY_BACKSPACE:
        if len(buffer) > 0:
            search_bar.delch(0, len(buffer) - buffer_offset - 1)
            buffer = buffer[:-1]
            if buffer_offset:
                buffer_offset -= 1
                search_bar.addstr(0, 0, buffer[buffer_offset:])
    elif c == 27:
        highlight = 0
        results_offset = 0
        buffer = ""
        resetSearchBar()
    else:
        highlight = 0
        buffer += chr(c)
        if len(buffer) >= search_bar.getmaxyx()[1]:
            search_bar.delch(0, 0)
            buffer_offset += 1
        search_bar.addch(0, len(buffer) - buffer_offset - 1, c)

    results = db.find(buffer)
    displayResults(results)

    return True
    

def kill():
    db.close()
    curses.nocbreak()
    screen.keypad(False)
    search_bar.keypad(False)
    curses.echo()
    curses.endwin()


def main(screen):
    init()

    while processKeyEvent():
        pass

    kill()


if __name__ == "__main__":
    wrapper(main)

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


def openResult(path):
    # TODO: Handle errors
    try:
        os.startfile(path)
    except:
        p = subprocess.Popen(["open", path], stdout=DEVNULL, stderr=STDOUT)


def displayResults(results, highlight, results_offset):
    # TODO: Show more details with Ctrl-D ? To see filename

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
    status_bar.keypad(True)

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    screen.clear()

    screen.addstr(0, 0,
            " Sheet Music Manager v0.1 - by Hugo Middeldorp ",
            curses.A_BOLD | curses.A_REVERSE)
    screen.refresh()

    updateStatus()


def updateStatus(status=":q to Quit | :u to Update library | Ctrl-E to Edit current entry"):
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
    status_bar.mvwin(num_rows - 1, 0)
    results_win.resize(num_rows - 4, num_cols)
    
    screen.clear()
    search_bar.clear()
    status_bar.clear()
    results_win.clear()

    screen.addstr(0, 0,
            " Sheet Music Manager v0.1 - by Hugo Middeldorp ",
            curses.A_BOLD | curses.A_REVERSE)
    screen.refresh()

    search_bar.move(0, 0)
    updateStatus()


def updateLibrary():
    screen.nodelay(True)
    file_names = db.getFileNames()
    percent = 0
    i = 0
    for file in file_names:
        char = screen.getch()
        if char == ord("c"):
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
    if percent < 100:
        updateStatus("Update cancelled, {}% complete".format(percent))
    else:
        updateStatus("Update complete")
    screen.nodelay(False)


def editEntry(path):
    # TODO: leave blank to keep the same as it currently is
    title = processKeyEvent(status_bar, "Title")
    if not title:
        updateStatus()
        return
    composer = processKeyEvent(status_bar, "Composer")
    if not composer:
        updateStatus()
        return

    updates = {"title": title, "composer": composer}
    db.editEntry(path, updates)
    updateStatus()


def processKeyEvent(win, sample="Type here to start..."):
    global search_bar, status_bar, num_rows
    
    win.erase()
    win.addstr(0, 0, sample, curses.A_DIM)
    win.refresh()
    win.move(0, 0)

    buffer = ""
    highlight = 0
    results_offset = 0
    buffer_offset = 0

    while True:
        if win == search_bar:
            results = db.find(buffer)
            displayResults(results, highlight, results_offset)
            search_len = len(results)

        # TODO: Problem with entering special characters eg. ó
        #       looks like get_wch() might be the answer
        c = win.get_wch()

        if buffer == "":
            win.erase()

        if c == '\n':
            if buffer.startswith(":"):
                return buffer
            elif win == search_bar:
                path = results[highlight + results_offset][2]
                return ":o/{}".format(path)
            return buffer
        elif c == curses.KEY_RESIZE:
            screenResize()
            return ""
        elif c == curses.KEY_MOUSE or c == curses.KEY_LEFT or c == curses.KEY_RIGHT:
            pass
        elif c == curses.KEY_BACKSPACE:
            if len(buffer) > 0:
                win.delch(0, len(buffer) - buffer_offset - 1)
                buffer = buffer[:-1]
                if buffer_offset:
                    buffer_offset -= 1
                    win.addstr(0, 0, buffer[buffer_offset:])
        elif curses.ascii.unctrl(c) == "^[":
            return ""
        elif curses.ascii.unctrl(c) == "^E" and win == search_bar:
            path = results[highlight + results_offset][2]
            return ":e/{}".format(path)
        elif c == curses.KEY_DOWN and win == search_bar: 
            # TODO: ERROR Type text and use arrows,
            #       the cursor goes down to last result
            if highlight < search_len - results_offset - 1:
                if highlight >= num_rows - 8:
                    results_offset += 1
                else: highlight += 1
        elif c == curses.KEY_UP and win == search_bar:
            if highlight > 0: 
                highlight -= 1
            elif results_offset > 0:
                results_offset -= 1
        elif isinstance(c, int):
            pass
        else:
            highlight = 0
            results_offset = 0
            buffer += c
            if len(buffer) >= win.getmaxyx()[1]:
                win.delch(0, 0)
                buffer_offset += 1
            win.addstr(0, len(buffer) - buffer_offset - 1, c, curses.A_NORMAL)


def kill():
    db.close()
    curses.nocbreak()
    screen.keypad(False)
    search_bar.keypad(False)
    curses.echo()
    curses.endwin()


def main(screen):
    init()

    buffer = ""

    while buffer != ":q":
        buffer = processKeyEvent(search_bar)
        
        if buffer == ":u":
            updateLibrary()
        elif buffer.startswith(":e/"):
            editEntry(buffer[3:])
        elif buffer.startswith(":o/"):
            openResult(buffer[3:])

    kill()


if __name__ == "__main__":
    wrapper(main)

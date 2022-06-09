import curses
from curses import wrapper


def init():
    global screen, search_bar, num_rows, num_cols, buffer

    screen = curses.initscr()
    num_rows, num_cols = screen.getmaxyx()
    search_bar = curses.newwin(1, num_cols, 1, 0)
    buffer = ""

    curses.start_color()
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    screen.clear()

    screen.addstr(0, 0,
            " Sheet Music Manager v 0.1 - by Hugo Middeldorp ",
            curses.A_BOLD | curses.A_REVERSE)
    screen.refresh()


def processKeyEvent():
    global buffer
    c = search_bar.getkey()
    buffer += c

    if buffer == ":q\n":
        return False

    if c == "\n":
        buffer = ""
        search_bar.clear()
        search_bar.refresh()
        screen.refresh
    elif c == "KEY_RESIZE":
        num_rows, num_cols = screen.getmaxyx()
    else:
        search_bar.addch(0, len(buffer) - 1, c)

    return True
    


def kill():
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()


def main(screen):
    init()

    while processKeyEvent():
        pass

    kill()


if __name__ == "__main__":
    wrapper(main)
